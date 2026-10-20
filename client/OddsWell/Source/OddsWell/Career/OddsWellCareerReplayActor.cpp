#include "Career/OddsWellCareerReplayActor.h"

#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

namespace
{
	constexpr float CareerPresentationSeconds = 180.0f;
	constexpr float CareerMarkerScaleXY = 0.5f;
	constexpr float CareerMarkerScaleZ = 1.4f;
}

AOddsWellCareerReplayActor::AOddsWellCareerReplayActor()
{
	PrimaryActorTick.bCanEverTick = true;
	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	BroadcastCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("BroadcastCamera"));
	BroadcastCamera->SetupAttachment(SceneRoot);
	BroadcastCamera->SetRelativeLocation(FVector(2400.0, -3000.0, 1800.0));
	BroadcastCamera->SetRelativeRotation(FRotator(-25.0, 129.0, 0.0));
	BroadcastCamera->FieldOfView = 55.0f;

	Scoreboard = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Scoreboard"));
	Scoreboard->SetupAttachment(SceneRoot);
	Scoreboard->SetRelativeLocation(FVector(0.0, -1250.0, 380.0));
	Scoreboard->SetRelativeRotation(FRotator(0.0, -45.0, 0.0));
	Scoreboard->SetHorizontalAlignment(EHTA_Center);
	Scoreboard->SetWorldSize(40.0f);
	Scoreboard->SetTextRenderColor(FColor::White);
}

bool AOddsWellCareerReplayActor::StartGame(const int32 GameId, FString& OutError)
{
	const UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	if (!Career || !Career->BuildReplay(GameId, Replay, OutError))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The career is not loaded.");
		}
		return false;
	}
	FrameInterval = CareerPresentationSeconds / FMath::Max(1, Replay.Frames.Num());
	CreateMarkers();
	if (APlayerController* Controller = GetWorld()->GetFirstPlayerController())
	{
		Controller->SetViewTarget(this);
		EnableInput(Controller);
		if (InputComponent)
		{
			InputComponent->BindKey(EKeys::S, IE_Pressed, this, &AOddsWellCareerReplayActor::SkipToFinal);
			InputComponent->BindKey(EKeys::Gamepad_FaceButton_Top, IE_Pressed, this, &AOddsWellCareerReplayActor::SkipToFinal);
		}
	}
	bStarted = true;
	DisplayFrame(0);
	NextFrame = 1;
	UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_REPLAY|game=%d|frames=%d|home=%s|away=%s|final=%d-%d|resimulated_from_frozen_inputs=true"),
		GameId, Replay.Frames.Num(), *Replay.HomeTeam, *Replay.AwayTeam, Replay.HomeScore, Replay.AwayScore);
	return true;
}

void AOddsWellCareerReplayActor::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bStarted || bComplete)
	{
		return;
	}
	Accumulator += DeltaSeconds;
	while (Accumulator >= FrameInterval && NextFrame < Replay.Frames.Num())
	{
		Accumulator -= FrameInterval;
		DisplayFrame(NextFrame++);
	}
}

void AOddsWellCareerReplayActor::SkipToFinal()
{
	if (!bStarted || bComplete || Replay.Frames.IsEmpty())
	{
		return;
	}
	NextFrame = Replay.Frames.Num();
	DisplayFrame(Replay.Frames.Num() - 1);
}

const FOddsWellCareerReplayFrame* AOddsWellCareerReplayActor::GetCurrentFrame() const
{
	return Replay.Frames.IsValidIndex(CurrentFrame) ? &Replay.Frames[CurrentFrame] : nullptr;
}

float AOddsWellCareerReplayActor::GetProgress() const
{
	return Replay.Frames.Num() ? static_cast<float>(CurrentFrame + 1) / Replay.Frames.Num() : 0.0f;
}

void AOddsWellCareerReplayActor::CreateMarkers()
{
	UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!Cylinder || !Cube)
	{
		return;
	}
	const FVector Locations[] = {
		{-1000.0, -500.0, 80.0}, {-1000.0, 0.0, 80.0}, {-1000.0, 500.0, 80.0},
		{-450.0, -300.0, 80.0}, {-450.0, 300.0, 80.0}, {-1300.0, 1000.0, 80.0},
		{1000.0, -500.0, 80.0}, {1000.0, 0.0, 80.0}, {1000.0, 500.0, 80.0},
		{450.0, -300.0, 80.0}, {450.0, 300.0, 80.0}, {1300.0, 1000.0, 80.0}
	};
	TArray<FString> Players = Replay.HomePlayers;
	Players.Append(Replay.AwayPlayers);
	for (int32 Index = 0; Index < Players.Num() && Index < UE_ARRAY_COUNT(Locations); ++Index)
	{
		const bool bHome = Index < Replay.HomePlayers.Num();
		UStaticMeshComponent* Marker = NewObject<UStaticMeshComponent>(this, *FString::Printf(TEXT("CareerMarker_%02d"), Index + 1));
		Marker->SetupAttachment(SceneRoot);
		Marker->SetStaticMesh(bHome ? Cylinder : Cube);
		Marker->SetRelativeLocation(Locations[Index]);
		Marker->SetRelativeScale3D(FVector(CareerMarkerScaleXY, CareerMarkerScaleXY, CareerMarkerScaleZ));
		Marker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		AddInstanceComponent(Marker);
		Marker->RegisterComponent();

		UTextRenderComponent* Label = NewObject<UTextRenderComponent>(this, *FString::Printf(TEXT("CareerLabel_%02d"), Index + 1));
		Label->SetupAttachment(SceneRoot);
		Label->SetRelativeLocation(Locations[Index] + FVector(0.0, 0.0, 150.0));
		Label->SetRelativeRotation(FRotator(0.0, -50.0, 0.0));
		Label->SetHorizontalAlignment(EHTA_Center);
		Label->SetWorldSize(28.0f);
		Label->SetTextRenderColor(bHome ? FColor(60, 190, 255) : FColor(255, 150, 60));
		Label->SetText(FText::FromString(Players[Index]));
		AddInstanceComponent(Label);
		Label->RegisterComponent();

		PlayerMarkerIndices.Add(Players[Index], Index);
		MarkerLocations.Add(Locations[Index]);
		Markers.Add(Marker);
	}
}

void AOddsWellCareerReplayActor::SetMarkerState(const FString& PlayerName, const float Scale, const float HeightOffset)
{
	if (const int32* Index = PlayerMarkerIndices.Find(PlayerName))
	{
		Markers[*Index]->SetRelativeScale3D(FVector(CareerMarkerScaleXY * Scale, CareerMarkerScaleXY * Scale, CareerMarkerScaleZ * Scale));
		Markers[*Index]->SetRelativeLocation(MarkerLocations[*Index] + FVector(0.0, 0.0, HeightOffset));
	}
}

void AOddsWellCareerReplayActor::DisplayFrame(const int32 FrameIndex)
{
	if (!Replay.Frames.IsValidIndex(FrameIndex))
	{
		return;
	}
	CurrentFrame = FrameIndex;
	for (int32 Index = 0; Index < Markers.Num(); ++Index)
	{
		Markers[Index]->SetRelativeScale3D(FVector(CareerMarkerScaleXY, CareerMarkerScaleXY, CareerMarkerScaleZ));
		Markers[Index]->SetRelativeLocation(MarkerLocations[Index]);
	}
	const FOddsWellCareerReplayFrame& Frame = Replay.Frames[FrameIndex];
	SetMarkerState(Frame.Actor, 1.5f, 60.0f);
	SetMarkerState(Frame.Target, 1.25f, 35.0f);
	Scoreboard->SetText(FText::FromString(FString::Printf(TEXT("%s %d - %d %s"), *Replay.AwayTeam, Frame.AwayScore, Frame.HomeScore, *Replay.HomeTeam)));
	if (Frame.Kind == TEXT("final"))
	{
		bComplete = true;
		UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_REPLAY_COMPLETE|game=%d|final=%d-%d|frames_shown_to=%d"), Replay.GameId, Frame.HomeScore, Frame.AwayScore, FrameIndex + 1);
	}
}
