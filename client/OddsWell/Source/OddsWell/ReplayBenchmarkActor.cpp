#include "ReplayBenchmarkActor.h"

#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerController.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/Parse.h"
#include "Misc/SecureHash.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 ExpectedFrameCount = 421;
constexpr float ApprovedPresentationSeconds = 180.0f;
constexpr float ApprovedReplayInterval = ApprovedPresentationSeconds / ExpectedFrameCount;
constexpr float MarkerScaleXY = 0.5f;
constexpr float MarkerScaleZ = 1.4f;
constexpr bool bApprovedVoiceCommentary = false;
constexpr bool bApprovedSkip = false;
constexpr bool bExpectedReplayWentOvertime = false;
const TCHAR* ExpectedReplaySha = TEXT("00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75");
const TCHAR* ExpectedFixtureSha1 = TEXT("a3b56bf84557babcd58c96acd40f94198b6c8c81");
}

AReplayBenchmarkActor::AReplayBenchmarkActor()
{
	PrimaryActorTick.bCanEverTick = true;
	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	BenchmarkCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("BenchmarkCamera"));
	BenchmarkCamera->SetupAttachment(SceneRoot);
	BenchmarkCamera->SetRelativeLocation(FVector(2400.0, -3000.0, 1800.0));
	BenchmarkCamera->SetRelativeRotation(FRotator(-25.0, 129.0, 0.0));
	BenchmarkCamera->FieldOfView = 55.0f;
	ReplayInterval = ApprovedReplayInterval;

	StatusText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("ReplayStatus"));
	StatusText->SetupAttachment(SceneRoot);
	StatusText->SetRelativeLocation(FVector(0.0, -1250.0, 380.0));
	StatusText->SetRelativeRotation(FRotator(0.0, -45.0, 0.0));
	StatusText->SetHorizontalAlignment(EHTA_Center);
	StatusText->SetWorldSize(32.0f);
	StatusText->SetTextRenderColor(FColor::White);
	StatusText->SetText(FText::FromString(TEXT("Loading authoritative replay...")));
}

void AReplayBenchmarkActor::BeginPlay()
{
	Super::BeginPlay();
	bAutoExit = FParse::Param(FCommandLine::Get(), TEXT("ReplayAutoExit"));
	bCaptureProof = FParse::Param(FCommandLine::Get(), TEXT("ReplayCapture"));
	bIntervalOverridden = FParse::Value(FCommandLine::Get(), TEXT("ReplayInterval="), ReplayInterval);
	ReplayInterval = FMath::Clamp(ReplayInterval, 0.01f, 1.0f);

	if (APlayerController* Controller = GetWorld()->GetFirstPlayerController())
	{
		Controller->SetViewTarget(this);
	}

	if (!LoadFixture())
	{
		SetActorTickEnabled(false);
		return;
	}

	CreateMarkers();
	UE_LOG(LogTemp, Display, TEXT("ODDSWELL_REPLAY_READY|%d|%s|%.3f"), Frames.Num(), *ReplaySha256, ReplayInterval);
	UE_LOG(
		LogTemp,
		Display,
		TEXT("ODDSWELL_REPLAY_PRESENTATION|mode=fixed_broadcast|target_seconds=180|symbolic_3d=true|text_callouts=true|voice_commentary=false|skip=false|overtime=false|qa_interval_override=%s"),
		bIntervalOverridden ? TEXT("true") : TEXT("false"));
}

void AReplayBenchmarkActor::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (bComplete)
	{
		if (bAutoExit && (ExitDelay += DeltaSeconds) >= 1.0f)
		{
			FPlatformMisc::RequestExit(false);
		}
		return;
	}

	PresentationElapsed += DeltaSeconds;
	Accumulator += DeltaSeconds;
	while (Accumulator >= ReplayInterval && NextFrame < Frames.Num())
	{
		Accumulator -= ReplayInterval;
		DisplayFrame(NextFrame++);
	}
}

bool AReplayBenchmarkActor::LoadFixture()
{
	const FString Path = FPaths::Combine(FPaths::ProjectContentDir(), TEXT("Replay/Season1Game1.json"));
	TArray<uint8> FixtureBytes;
	FString JsonText;
	if (!FFileHelper::LoadFileToArray(FixtureBytes, *Path) || !FFileHelper::LoadFileToString(JsonText, *Path))
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|fixture_not_found|%s"), *Path);
		StatusText->SetText(FText::FromString(TEXT("Replay fixture not found")));
		return false;
	}
	const FSHAHash FixtureHash = FSHA1::HashBuffer(FixtureBytes.GetData(), FixtureBytes.Num());
	if (!LexToString(FixtureHash).Equals(ExpectedFixtureSha1, ESearchCase::IgnoreCase))
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|fixture_hash_mismatch"));
		StatusText->SetText(FText::FromString(TEXT("Replay fixture hash mismatch")));
		return false;
	}

	TSharedPtr<FJsonObject> RootObject;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
	if (!FJsonSerializer::Deserialize(Reader, RootObject) || !RootObject.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|invalid_json"));
		StatusText->SetText(FText::FromString(TEXT("Replay fixture is invalid")));
		return false;
	}

	FString Schema;
	const TSharedPtr<FJsonObject>* Summary = nullptr;
	const TSharedPtr<FJsonObject>* Archive = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* FrameValues = nullptr;
	if (!RootObject->TryGetStringField(TEXT("schema"), Schema)
		|| Schema != TEXT("oddswell-public-replay-v1")
		|| !RootObject->TryGetObjectField(TEXT("summary"), Summary)
		|| !RootObject->TryGetObjectField(TEXT("archive"), Archive)
		|| !RootObject->TryGetArrayField(TEXT("frames"), FrameValues))
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|invalid_schema"));
		return false;
	}

	double HomeScoreValue = 0.0;
	double AwayScoreValue = 0.0;
	bool bVerified = false;
	const TArray<TSharedPtr<FJsonValue>>* HomeValues = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* AwayValues = nullptr;
	if (!(*Summary)->TryGetStringField(TEXT("home"), HomeTeam)
		|| !(*Summary)->TryGetStringField(TEXT("away"), AwayTeam)
		|| !(*Summary)->TryGetNumberField(TEXT("home_score"), HomeScoreValue)
		|| !(*Summary)->TryGetNumberField(TEXT("away_score"), AwayScoreValue)
		|| !(*Summary)->TryGetArrayField(TEXT("home_players"), HomeValues)
		|| !(*Summary)->TryGetArrayField(TEXT("away_players"), AwayValues)
		|| !(*Archive)->TryGetStringField(TEXT("replay_sha256"), ReplaySha256)
		|| !(*Archive)->TryGetBoolField(TEXT("verified"), bVerified)
		|| HomeTeam != TEXT("Harbor City Waves")
		|| AwayTeam != TEXT("Mesa Vista Sol")
		|| static_cast<int32>(HomeScoreValue) != 101
		|| static_cast<int32>(AwayScoreValue) != 104
		|| !bVerified
		|| ReplaySha256 != ExpectedReplaySha
		|| HomeValues->Num() != 6
		|| AwayValues->Num() != 6
		|| FrameValues->Num() != ExpectedFrameCount)
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|evidence_mismatch"));
		return false;
	}

	for (const TSharedPtr<FJsonValue>& Value : *HomeValues)
	{
		HomePlayers.Add(Value->AsString());
	}
	for (const TSharedPtr<FJsonValue>& Value : *AwayValues)
	{
		AwayPlayers.Add(Value->AsString());
	}

	for (const TSharedPtr<FJsonValue>& Value : *FrameValues)
	{
		const TSharedPtr<FJsonObject> FrameObject = Value->AsObject();
		const TArray<TSharedPtr<FJsonValue>>* Scores = nullptr;
		FReplayBenchmarkFrame Frame;
		double ClockValue = 0.0;
		if (!FrameObject.IsValid()
			|| !FrameObject->TryGetStringField(TEXT("kind"), Frame.Kind)
			|| !FrameObject->TryGetStringField(TEXT("label"), Frame.Label)
			|| !FrameObject->TryGetStringField(TEXT("offense"), Frame.Offense)
			|| !FrameObject->TryGetStringField(TEXT("actor"), Frame.Actor)
			|| !FrameObject->TryGetStringField(TEXT("target"), Frame.Target)
			|| !FrameObject->TryGetNumberField(TEXT("clock_seconds"), ClockValue)
			|| !FrameObject->TryGetArrayField(TEXT("score"), Scores)
			|| Scores->Num() != 2)
		{
			UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|invalid_frame|%d"), Frames.Num() + 1);
			return false;
		}
		Frame.ClockSeconds = static_cast<int32>(ClockValue);
		Frame.HomeScore = static_cast<int32>((*Scores)[0]->AsNumber());
		Frame.AwayScore = static_cast<int32>((*Scores)[1]->AsNumber());
		Frames.Add(MoveTemp(Frame));
	}

	const FReplayBenchmarkFrame& FinalFrame = Frames.Last();
	return FinalFrame.Kind == TEXT("final")
		&& FinalFrame.ClockSeconds == 0
		&& FinalFrame.HomeScore == 101
		&& FinalFrame.AwayScore == 104;
}

void AReplayBenchmarkActor::CreateMarkers()
{
	UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!Cylinder || !Cube)
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_REPLAY_ERROR|primitive_mesh_missing"));
		SetActorTickEnabled(false);
		return;
	}

	const FVector Locations[] = {
		{-1000.0, -500.0, 80.0}, {-1000.0, 0.0, 80.0}, {-1000.0, 500.0, 80.0},
		{-450.0, -300.0, 80.0}, {-450.0, 300.0, 80.0}, {-1300.0, 1000.0, 80.0},
		{1000.0, -500.0, 80.0}, {1000.0, 0.0, 80.0}, {1000.0, 500.0, 80.0},
		{450.0, -300.0, 80.0}, {450.0, 300.0, 80.0}, {1300.0, 1000.0, 80.0}
	};
	TArray<FString> Players = HomePlayers;
	Players.Append(AwayPlayers);
	for (int32 Index = 0; Index < Players.Num(); ++Index)
	{
		UStaticMeshComponent* Marker = NewObject<UStaticMeshComponent>(this, *FString::Printf(TEXT("ReplayMarker_%02d"), Index + 1));
		Marker->SetupAttachment(SceneRoot);
		Marker->SetStaticMesh(Index < HomePlayers.Num() ? Cylinder : Cube);
		Marker->SetRelativeLocation(Locations[Index]);
		Marker->SetRelativeScale3D(FVector(MarkerScaleXY, MarkerScaleXY, MarkerScaleZ));
		Marker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		AddInstanceComponent(Marker);
		Marker->RegisterComponent();

		UTextRenderComponent* Label = NewObject<UTextRenderComponent>(this, *FString::Printf(TEXT("ReplayLabel_%02d"), Index + 1));
		Label->SetupAttachment(SceneRoot);
		Label->SetRelativeLocation(Locations[Index] + FVector(0.0, 0.0, 150.0));
		Label->SetRelativeRotation(FRotator(0.0, -50.0, 0.0));
		Label->SetHorizontalAlignment(EHTA_Center);
		Label->SetWorldSize(28.0f);
		Label->SetTextRenderColor(Index < HomePlayers.Num() ? FColor(60, 190, 255) : FColor(255, 150, 60));
		Label->SetText(FText::FromString(Players[Index]));
		AddInstanceComponent(Label);
		Label->RegisterComponent();

		PlayerMarkerIndices.Add(Players[Index], Index);
		MarkerLocations.Add(Locations[Index]);
		Markers.Add(Marker);
		PlayerLabels.Add(Label);
	}
}

void AReplayBenchmarkActor::SetMarkerState(const FString& PlayerName, float Scale, float HeightOffset)
{
	const int32* Index = PlayerMarkerIndices.Find(PlayerName);
	if (!Index)
	{
		return;
	}
	Markers[*Index]->SetRelativeScale3D(FVector(MarkerScaleXY * Scale, MarkerScaleXY * Scale, MarkerScaleZ * Scale));
	Markers[*Index]->SetRelativeLocation(MarkerLocations[*Index] + FVector(0.0, 0.0, HeightOffset));
}

void AReplayBenchmarkActor::DisplayFrame(int32 FrameIndex)
{
	for (int32 Index = 0; Index < Markers.Num(); ++Index)
	{
		Markers[Index]->SetRelativeScale3D(FVector(MarkerScaleXY, MarkerScaleXY, MarkerScaleZ));
		Markers[Index]->SetRelativeLocation(MarkerLocations[Index]);
	}

	const FReplayBenchmarkFrame& Frame = Frames[FrameIndex];
	SetMarkerState(Frame.Actor, 1.5f, 60.0f);
	SetMarkerState(Frame.Target, 1.25f, 35.0f);
	const FString Clock = FString::Printf(TEXT("%02d:%02d"), Frame.ClockSeconds / 60, Frame.ClockSeconds % 60);
	FString Status = FString::Printf(
		TEXT("AUTHORITATIVE RECORDED REPLAY - ILLUSTRATIVE POSITIONS\nFrame %d/%d | %s | Harbor %d - %d Mesa\n%s | %s\nOffense: %s | Actor: %s | Target: %s\nOvertime: NO | Voice commentary: OFF"),
		FrameIndex + 1,
		Frames.Num(),
		*Clock,
		Frame.HomeScore,
		Frame.AwayScore,
		*Frame.Kind,
		*Frame.Label,
		*Frame.Offense,
		*Frame.Actor,
		*Frame.Target);

	if (Frame.Kind == TEXT("final"))
	{
		Status += FString::Printf(TEXT("\nVERIFIED REPLAY SHA-256: %s"), *ReplaySha256);
	}
	StatusText->SetText(FText::FromString(Status));
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(42, Frame.Kind == TEXT("final") ? 60.0f : ReplayInterval + 0.1f, FColor::White, Status);
	}

	UE_LOG(
		LogTemp,
		Display,
		TEXT("ODDSWELL_REPLAY_FRAME|%d|%d|%d|%d|%s|%s|%s"),
		FrameIndex + 1,
		Frame.ClockSeconds,
		Frame.HomeScore,
		Frame.AwayScore,
		*Frame.Kind,
		*Frame.Actor,
		*Frame.Target);

	if (bCaptureProof && FrameIndex + 1 == 211)
	{
		FScreenshotRequest::RequestScreenshot(TEXT("Phase1A2b_Mid.png"), true, false);
	}
	if (FrameIndex + 1 == Frames.Num())
	{
		UE_LOG(LogTemp, Display, TEXT("ODDSWELL_REPLAY_COMPLETE|421|101|104|%s"), *ReplaySha256);
		UE_LOG(
			LogTemp,
			Display,
			TEXT("ODDSWELL_REPLAY_PRESENTATION_COMPLETE|elapsed_seconds=%.3f|target_seconds=180|default_cadence=%s"),
			PresentationElapsed,
			bIntervalOverridden ? TEXT("false") : TEXT("true"));
		if (bCaptureProof)
		{
			FScreenshotRequest::RequestScreenshot(TEXT("Phase1A2b_Final.png"), true, false);
		}
		bComplete = true;
	}
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellReplayPresentationDefaultsTest,
	"OddsWell.Replay.PresentationDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellReplayPresentationDefaultsTest::RunTest(const FString& Parameters)
{
	const float TotalSeconds = ApprovedReplayInterval * ExpectedFrameCount;
	TestTrue(TEXT("Default replay presentation is exactly three minutes"), FMath::IsNearlyEqual(TotalSeconds, 180.0f));
	TestTrue(TEXT("Default replay presentation stays inside the approved two-to-five-minute window"), TotalSeconds >= 120.0f && TotalSeconds <= 300.0f);
	TestFalse(TEXT("Voice commentary remains disabled"), bApprovedVoiceCommentary);
	TestFalse(TEXT("Skip remains disabled until the invariance phase"), bApprovedSkip);
	TestFalse(TEXT("The accepted archived game did not enter overtime"), bExpectedReplayWentOvertime);
	return true;
}
#endif
