#include "PlaceholderLocomotion.h"

#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "CharacterAppearanceSave.h"
#include "CharacterPresetCatalog.h"
#include "CanonicalActiveGameExecutionCommitment.h"
#include "CanonicalMatchWinnerOffer.h"
#include "CanonicalPregameCommitment.h"
#include "CanonicalScheduledGame.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Canvas.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HousingTierCatalog.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Engine.h"
#include "Engine/PointLight.h"
#include "Components/PointLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Net/UnrealNetwork.h"
#include "PublicLeagueView.h"
#include "ReplayBenchmarkActor.h"
#include "StudioHomeSave.h"
#include "UnrealClient.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogOddsWellLocomotion, Log, All);

namespace
{
constexpr float WalkSpeed = 260.0f;
constexpr float RunSpeed = 520.0f;
constexpr float JumpVelocity = 520.0f;
constexpr float CameraDistance = 420.0f;
constexpr float CameraPitchMin = -65.0f;
constexpr float CameraPitchMax = 65.0f;
constexpr float CapsuleRadius = 42.0f;
constexpr float CapsuleHalfHeight = 96.0f;
constexpr float SharedCitySpawnSpacing = 200.0f;
constexpr float SharedCityQaMovementDistance = 300.0f;
constexpr int32 SharedCityCapacityMinClients = 2;
constexpr int32 SharedCityCapacityMaxClients = 4;
constexpr ECollisionResponse SharedCityPlayerCollision = ECR_Ignore;
constexpr bool AllowCrouch = false;
constexpr bool AllowFlight = false;
constexpr bool AllowSwimming = false;
constexpr bool UseCameraCollision = true;
const FVector SafeSpawnLocation(0.0, 0.0, 220.0);
const FLinearColor StarterOffWhite(0.92f, 0.90f, 0.82f);
const FName TopComponentName(TEXT("StarterOutfitTop"));
const FName BottomComponentName(TEXT("StarterOutfitBottom"));
constexpr float SundaleRouteDistance = 80000.0f;
constexpr float SundaleWaypointTolerance = 75.0f;
constexpr float JobInteractionRadius = 350.0f;
constexpr float StudioEntryRadius = 350.0f;
constexpr float StudioQaWalkDistance = 200.0f;
constexpr float StadiumEntryRadius = 350.0f;
constexpr float SportsbookInteractionRadius = 350.0f;
constexpr int64 CanonicalProbabilityScale = 100000000;
constexpr float StadiumQaWaypointTolerance = 75.0f;
const FName StudioStructureTag(TEXT("OddsWellStudioStructure"));
const FName StudioFurnitureTag(TEXT("OddsWellStudioFurniture"));
const FName StadiumStructureTag(TEXT("OddsWellStadiumStructure"));
const FName StadiumZoneTag(TEXT("OddsWellStadiumZone"));
const FVector JobInteractionLocation(9500.0, 0.0, 0.0);
const FVector StadiumEntranceThreshold(7000.0, 18000.0, 0.0);
const FVector SportsbookInteractionLocation(1000.0, 18000.0, 0.0);
const TCHAR* TicketBoothOpenPrompt = TEXT("Press E to open betting odds");
constexpr int32 TicketBoothMarketPageCount = 4;
FVector StadiumCityReturnLocation = StadiumEntranceThreshold + FVector(0.0, -100.0, SafeSpawnLocation.Z);
const FVector StadiumInteriorSpawn(-1600.0, 0.0, 220.0);
const FVector StadiumReplayOrigin(350.0, 0.0, 0.0);
constexpr float StadiumReplayScale = 0.15f;
constexpr int64 JobRecoveryQaStartUnixSeconds = 2000000000;
int32 StudioQaProcessStage = 0;
int32 StadiumQaProcessStage = 0;

const TArray<FString>& GetTicketBoothMarketLabels()
{
	static const TArray<FString> Labels = {
		TEXT("GAME LINES"),
		TEXT("MARGIN"),
		TEXT("OVERTIME"),
		TEXT("PLAYER PROPS"),
	};
	return Labels;
}

FString BuildCanonicalSettledLossReceiptText(
	const FOddsWellCanonicalSettledLossReceipt& Receipt)
{
	return FString::Printf(
		TEXT("BET SETTLED \u2014 %s\n%s selected\nStake %lld Odds Bucks\nFinal Harbor %d\u2013%d Mesa\nWinner %s\nReturned %lld\nNet %+lld\nBalance %lld\nE or ESC: CLOSE"),
		Receipt.Outcome == FName(TEXT("won")) ? TEXT("WIN") : TEXT("LOSS"),
		*Receipt.SelectedTeam,
		Receipt.Stake,
		Receipt.HomeScore,
		Receipt.AwayScore,
		*Receipt.Winner,
		Receipt.Returned,
		Receipt.Net,
		Receipt.CurrentBalance);
}

bool BuildSettledLossHandoffCue(
	const bool bReceiptValid,
	const FString& MapName,
	const FVector& PlayerLocation,
	const float FacingYaw,
	const bool bMenuOpen,
	const bool bInStudio,
	const bool bInStadium,
	FString& OutCue)
{
	OutCue.Reset();
	const FVector2D ToBooth(
		SportsbookInteractionLocation.X - PlayerLocation.X,
		SportsbookInteractionLocation.Y - PlayerLocation.Y);
	const float Distance = ToBooth.Size();
	if (!bReceiptValid
		|| !MapName.Contains(TEXT("SundaleGraybox"))
		|| bMenuOpen
		|| bInStudio
		|| bInStadium
		|| Distance <= SportsbookInteractionRadius)
	{
		return false;
	}

	const float FacingRadians = FMath::DegreesToRadians(FacingYaw);
	const FVector2D Forward(FMath::Cos(FacingRadians), FMath::Sin(FacingRadians));
	const FVector2D Right(-Forward.Y, Forward.X);
	const FVector2D Direction = ToBooth / Distance;
	const float ForwardDot = FVector2D::DotProduct(Direction, Forward);
	const float RightDot = FVector2D::DotProduct(Direction, Right);
	const TCHAR* RelativeDirection = FMath::Abs(ForwardDot) >= FMath::Abs(RightDot)
		? (ForwardDot >= 0.0f ? TEXT("AHEAD") : TEXT("BEHIND"))
		: (RightDot >= 0.0f ? TEXT("RIGHT") : TEXT("LEFT"));
	OutCue = FString::Printf(
		TEXT("SETTLED BET READY \u2014 TICKET BOOTH: %s \u2014 %d m"),
		RelativeDirection,
		FMath::RoundToInt(Distance / 100.0f));
	return true;
}

bool IsCanonicalBetSlipOfferUsable(
	const FOddsWellMatchWinnerOfferPreview& Offer)
{
	return Offer.Selections.Num() == 2
		&& Offer.MinimumStake == 10
		&& Offer.MaximumStake == 100
		&& Offer.StakeIncrement == 10
		&& Offer.Selections[0].Team == Offer.HomeTeam
		&& Offer.Selections[1].Team == Offer.AwayTeam
		&& Offer.Selections[0].WinProbabilityE8 > 0
		&& Offer.Selections[1].WinProbabilityE8 > 0
		&& Offer.Selections[0].DecimalOddsE4 > 0
		&& Offer.Selections[1].DecimalOddsE4 > 0;
}

int64 CalculateCanonicalBetSlipGrossReturn(
	const int64 Stake,
	const int64 WinProbabilityE8)
{
	return Stake > 0 && WinProbabilityE8 > 0
		? Stake * CanonicalProbabilityScale / WinProbabilityE8
		: 0;
}

bool ShouldShowCanonicalBetSlipReview(
	const bool bHasOffer,
	const bool bHasPendingReceipt,
	const bool bHasSettledReceipt)
{
	return bHasOffer && !bHasPendingReceipt && !bHasSettledReceipt;
}

bool IsCanonicalFortyPlacementEligible(
	const FOddsWellMatchWinnerOfferPreview& Offer,
	const int32 SelectionIndex,
	const int64 Stake,
	const int64 Balance)
{
	return IsCanonicalBetSlipOfferUsable(Offer)
		&& Offer.Selections.IsValidIndex(SelectionIndex)
		&& (Offer.Selections[SelectionIndex].Team == TEXT("Harbor City Waves")
			|| Offer.Selections[SelectionIndex].Team == TEXT("Mesa Vista Sol"))
		&& Stake == 40
		&& Balance >= Stake;
}

bool AdvanceCanonicalFortyConfirmation(
	const bool bEligible,
	bool& bArmed)
{
	if (!bEligible)
	{
		bArmed = false;
		return false;
	}
	if (!bArmed)
	{
		bArmed = true;
		return false;
	}
	bArmed = false;
	return true;
}

FString BuildCanonicalBetSlipReviewText(
	const FOddsWellMatchWinnerOfferPreview& Offer,
	const int32 SelectionIndex,
	const int64 Stake,
	const int64 CurrentBalance)
{
	if (!IsCanonicalBetSlipOfferUsable(Offer)
		|| Stake < Offer.MinimumStake
		|| Stake > Offer.MaximumStake
		|| (Stake - Offer.MinimumStake) % Offer.StakeIncrement != 0)
	{
		return TEXT("BET SLIP UNAVAILABLE");
	}
	if (!Offer.Selections.IsValidIndex(SelectionIndex))
	{
		return FString::Printf(
			TEXT("BET SLIP\nSELECT A TEAM\nSTAKE %lld Odds Bucks\nCURRENT BALANCE %lld Odds Bucks\nLOCKS AT GAME START\nREVIEW ONLY \u2014 WAGER NOT PLACED\nMOUSE: SELECT / - / +\nKEYBOARD: , / . TEAM   - / = STAKE\nCONTROLLER: D-PAD LEFT / RIGHT TEAM   UP / DOWN STAKE"),
			Stake,
			CurrentBalance);
	}
	const FOddsWellMatchWinnerSelectionPreview& Selection =
		Offer.Selections[SelectionIndex];
	return FString::Printf(
		TEXT("BET SLIP\n%s\nDECIMAL ODDS %.4f\nSTAKE %lld Odds Bucks\nPOTENTIAL GROSS RETURN %lld Odds Bucks\nCURRENT BALANCE %lld Odds Bucks\nLOCKS AT GAME START\nREVIEW ONLY \u2014 WAGER NOT PLACED\nMOUSE: SELECT / - / +\nKEYBOARD: , / . TEAM   - / = STAKE\nCONTROLLER: D-PAD LEFT / RIGHT TEAM   UP / DOWN STAKE"),
		*Selection.Team,
		static_cast<double>(Selection.DecimalOddsE4) / 10000.0,
		Stake,
		CalculateCanonicalBetSlipGrossReturn(
			Stake,
			Selection.WinProbabilityE8),
		CurrentBalance);
}

void ApplyTicketBoothEvidenceExpiry(
	const int64 ObservedServerUnixSeconds,
	const EOddsWellCanonicalPendingReceiptResult ReceiptResult,
	bool& bMenuVisible,
	TUniquePtr<FOddsWellMatchWinnerOfferPreview>& Offer,
	TUniquePtr<FOddsWellCanonicalPendingMatchWinnerReceipt>& Receipt)
{
	if (bMenuVisible
		&& Offer
		&& (ObservedServerUnixSeconds >= Offer->LockUnix
			|| (Receipt
				&& ReceiptResult
					!= EOddsWellCanonicalPendingReceiptResult::Ready)))
	{
		Receipt.Reset();
		Offer.Reset();
	}
}

bool ShouldScheduleCanonicalMatchWinnerTipoffLock(
	const bool bTimerExists,
	const int64 ObservedServerUnixSeconds,
	const int64 TipoffUnixSeconds)
{
	return !bTimerExists
		&& ObservedServerUnixSeconds > 0
		&& ObservedServerUnixSeconds < TipoffUnixSeconds;
}

bool IsExactCanonicalMatchWinnerTipoff(
	const int64 ObservedServerUnixSeconds,
	const int64 TipoffUnixSeconds)
{
	return ObservedServerUnixSeconds == TipoffUnixSeconds;
}

bool ShouldAttemptCanonicalMatchWinnerResultLink(
	const int32 PrivateResultFileCount)
{
	return PrivateResultFileCount > 0;
}

bool IsSameCanonicalMatchWinnerResultLink(
	const FOddsWellMatchWinnerResultLinkRecord& Left,
	const FOddsWellMatchWinnerResultLinkRecord& Right)
{
	return Left.ResultCommandId == Right.ResultCommandId
		&& Left.RequestCommandId == Right.RequestCommandId
		&& Left.LockCommandId == Right.LockCommandId
		&& Left.ResultSchema == Right.ResultSchema
		&& Left.ResultVersion == Right.ResultVersion
		&& Left.SeasonNumber == Right.SeasonNumber
		&& Left.GameNumber == Right.GameNumber
		&& Left.HomeTeam == Right.HomeTeam
		&& Left.AwayTeam == Right.AwayTeam
		&& Left.HomeScore == Right.HomeScore
		&& Left.AwayScore == Right.AwayScore
		&& Left.Winner == Right.Winner
		&& Left.ReplaySealSha256 == Right.ReplaySealSha256;
}

bool IsExactCurrentCanonicalMatchWinnerResultLink(
	const FOddsWellMatchWinnerResultLinkRecord& Result)
{
	const FString OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	return Result.ResultCommandId
			== TEXT("canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289")
		&& Result.RequestCommandId
			== TEXT("canonical:h26e:match_winner:request:") + OfferId
		&& Result.LockCommandId
			== TEXT("canonical:h26g:match_winner:lock:") + OfferId
		&& Result.ResultSchema
			== TEXT("oddswell-private-canonical-game-result-v1")
		&& Result.ResultVersion
			== TEXT("oddswell-private-game-result-recorder-v1")
		&& Result.SeasonNumber == 1
		&& Result.GameNumber == 1
		&& Result.HomeTeam == TEXT("Harbor City Waves")
		&& Result.AwayTeam == TEXT("Mesa Vista Sol")
		&& Result.HomeScore == 79
		&& Result.AwayScore == 113
		&& Result.Winner == Result.AwayTeam
		&& Result.ReplaySealSha256
			== TEXT("35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db");
}

bool IsExactCurrentCanonicalMatchWinnerLossDecision(
	const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
{
	const FString OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	const FString ResultSha =
		TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	return Decision.DecisionCommandId
			== TEXT("canonical:h26m:match_winner:decision:") + ResultSha
		&& Decision.RequestCommandId
			== TEXT("canonical:h26e:match_winner:request:") + OfferId
		&& Decision.LockCommandId
			== TEXT("canonical:h26g:match_winner:lock:") + OfferId
		&& Decision.ResultCommandId
			== TEXT("canonical:h26l:match_winner:result:") + ResultSha
		&& Decision.DecisionSchema
			== TEXT("oddswell-match-winner-settlement-decision-v1")
		&& Decision.DecisionVersion
			== TEXT("match-winner-settlement-decision-v1")
		&& Decision.OfferId == OfferId
		&& Decision.OfferVersion
			== TEXT("basketball-match-winner-odds-v1")
		&& Decision.SelectedTeam == TEXT("Harbor City Waves")
		&& Decision.AuthoritativeWinner == TEXT("Mesa Vista Sol")
		&& Decision.Stake == 40
		&& Decision.Outcome == FName(TEXT("lost"))
		&& Decision.GrossReturnDue == 0
		&& Decision.SelectedWinProbabilityE8 == 0
		&& Decision.PayoutFormula.IsEmpty()
		&& Decision.Status == FName(TEXT("decided_pending_apply"));
}

bool IsExactCurrentCanonicalMatchWinnerMesaWinDecision(
	const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
{
	const FString OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	const FString ResultSha =
		TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	return Decision.DecisionCommandId
			== TEXT("canonical:h26an:match_winner:win-decision:") + ResultSha
		&& Decision.RequestCommandId
			== TEXT("canonical:h26e:match_winner:request:") + OfferId
		&& Decision.LockCommandId
			== TEXT("canonical:h26g:match_winner:lock:") + OfferId
		&& Decision.ResultCommandId
			== TEXT("canonical:h26l:match_winner:result:") + ResultSha
		&& Decision.DecisionSchema
			== TEXT("oddswell-match-winner-settlement-decision-v1")
		&& Decision.DecisionVersion
			== TEXT("match-winner-settlement-decision-v1")
		&& Decision.OfferId == OfferId
		&& Decision.OfferVersion
			== TEXT("basketball-match-winner-odds-v1")
		&& Decision.SelectedTeam == TEXT("Mesa Vista Sol")
		&& Decision.AuthoritativeWinner == TEXT("Mesa Vista Sol")
		&& Decision.Stake == 40
		&& Decision.Outcome == FName(TEXT("won"))
		&& Decision.GrossReturnDue == 94
		&& Decision.SelectedWinProbabilityE8 == 42413307
		&& Decision.PayoutFormula
			== TEXT("floor(stake*100000000/win_probability_e8)")
		&& Decision.Status == FName(TEXT("decided_pending_apply"));
}

bool CanResumeCanonicalLossDecisionAfterResultLinkRejection(
	const FString& Error)
{
	return Error
		== TEXT("Canonical Match Winner result linking requires exact schema-12 H26E/H26G evidence and no downstream state.")
		|| Error
			== TEXT("Canonical Match Winner result prerequisites failed exact H26A/B/C/E/G validation.");
}

bool IsExactCurrentCanonicalMatchWinnerLossFinalization(
	const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
{
	const FString OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	const FString ResultSha =
		TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	return Finalization.FinalizationCommandId
			== TEXT("canonical:h26n:match_winner:finalization:") + ResultSha
		&& Finalization.DecisionCommandId
			== TEXT("canonical:h26m:match_winner:decision:") + ResultSha
		&& Finalization.RequestCommandId
			== TEXT("canonical:h26e:match_winner:request:") + OfferId
		&& Finalization.LockCommandId
			== TEXT("canonical:h26g:match_winner:lock:") + OfferId
		&& Finalization.ResultCommandId
			== TEXT("canonical:h26l:match_winner:result:") + ResultSha
		&& Finalization.FinalizationSchema
			== TEXT("oddswell-match-winner-loss-finalization-v1")
		&& Finalization.FinalizationVersion
			== TEXT("match-winner-loss-finalization-v1")
		&& Finalization.OfferId == OfferId
		&& Finalization.OfferVersion
			== TEXT("basketball-match-winner-odds-v1")
		&& Finalization.SelectedTeam == TEXT("Harbor City Waves")
		&& Finalization.AuthoritativeWinner == TEXT("Mesa Vista Sol")
		&& Finalization.Stake == 40
		&& Finalization.Outcome == FName(TEXT("lost"))
		&& Finalization.GrossReturnApplied == 0
		&& Finalization.Status == FName(TEXT("settled_lost"))
		&& Finalization.ObservedFinalBalance == 60
		&& Finalization.ObservedLedgerEntryCount == 2;
}

bool CanResumeCanonicalLossFinalizationAfterDecisionRejection(
	const FString& Error)
{
	return Error
		== TEXT("Canonical Match Winner loss decision requires exact schema-12 evidence and no later state.");
}

FString GetCanonicalGameExecutionHandoffPath()
{
	return FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("PrivateExecution"),
		TEXT("Handoff"),
		TEXT("OddsWellCanonicalActiveGameExecutionHandoff.json"));
}

struct FStudioSurfaceSpec
{
	FVector Location;
	FVector Scale;
};

const TArray<FStudioSurfaceSpec>& GetEmptyStudioSurfaces()
{
	static const TArray<FStudioSurfaceSpec> Surfaces = {
		{FVector(0.0, 0.0, -10.0), FVector(8.0, 6.0, 0.2)},
		{FVector(0.0, 0.0, 300.0), FVector(8.0, 6.0, 0.2)},
		{FVector(-400.0, 0.0, 145.0), FVector(0.2, 6.0, 2.9)},
		{FVector(400.0, 0.0, 145.0), FVector(0.2, 6.0, 2.9)},
		{FVector(0.0, -300.0, 145.0), FVector(8.0, 0.2, 2.9)},
		{FVector(0.0, 300.0, 145.0), FVector(8.0, 0.2, 2.9)},
	};
	return Surfaces;
}

struct FStadiumSurfaceSpec
{
	FName Id;
	FVector Location;
	FVector Scale;
};

const TArray<FStadiumSurfaceSpec>& GetStadiumSurfaces()
{
	static const TArray<FStadiumSurfaceSpec> Surfaces = {
		{TEXT("base_floor"), FVector(0.0, 0.0, -10.0), FVector(40.0, 24.0, 0.2)},
		{TEXT("court_floor"), FVector(350.0, 0.0, 1.0), FVector(14.0, 8.0, 0.02)},
		{TEXT("viewing_deck"), FVector(350.0, 900.0, 20.0), FVector(14.0, 2.0, 0.4)},
		{TEXT("viewing_row"), FVector(350.0, 1050.0, 55.0), FVector(14.0, 1.0, 0.7)},
		{TEXT("west_wall"), FVector(-2000.0, 0.0, 300.0), FVector(0.2, 24.0, 6.0)},
		{TEXT("east_wall"), FVector(2000.0, 0.0, 300.0), FVector(0.2, 24.0, 6.0)},
		{TEXT("north_wall"), FVector(0.0, 1200.0, 300.0), FVector(40.0, 0.2, 6.0)},
		{TEXT("south_wall"), FVector(0.0, -1200.0, 300.0), FVector(40.0, 0.2, 6.0)},
	};
	return Surfaces;
}

struct FStadiumZoneSpec
{
	FName Id;
	FString Label;
	FVector Location;
};

const TArray<FStadiumZoneSpec>& GetStadiumZones()
{
	static const TArray<FStadiumZoneSpec> Zones = {
		{TEXT("entry_concourse"), TEXT("ENTRY / CONCOURSE"), FVector(-1450.0, -400.0, 180.0)},
		{TEXT("court_floor"), TEXT("COURT FLOOR"), FVector(350.0, -250.0, 180.0)},
		{TEXT("public_viewing"), TEXT("PUBLIC VIEWING"), FVector(350.0, 650.0, 220.0)},
		{TEXT("future_presentation"), TEXT("ARCHIVED MATCH PRESENTATION"), FVector(1150.0, 0.0, 220.0)},
		{TEXT("exit"), TEXT("EXIT TO SUNDALE"), FVector(-1550.0, 400.0, 180.0)},
	};
	return Zones;
}

const TArray<FVector>& GetStadiumQaWaypoints()
{
	static const TArray<FVector> Waypoints = {
		FVector(-1000.0, 0.0, 0.0),
		FVector(350.0, 0.0, 0.0),
		FVector(350.0, 600.0, 0.0),
		FVector(1150.0, 0.0, 0.0),
		FVector(-1500.0, 0.0, 0.0),
	};
	return Waypoints;
}

bool MatchesSharedCityReconnectAppearance(
	const FOddsWellSharedCityAppearance& Expected,
	const FOddsWellSharedCityAppearance& Actual)
{
	return Expected.bOwnerSubmitted
		&& Actual.bOwnerSubmitted
		&& Expected.PresetId == Actual.PresetId
		&& Expected.TopItemId == Actual.TopItemId
		&& Expected.BottomItemId == Actual.BottomItemId;
}

int32 GetSharedCityQaTargetClients()
{
	int32 TargetClients = SharedCityCapacityMinClients;
	FParse::Value(FCommandLine::Get(), TEXT("SharedCityQaClients="), TargetClients);
	return FMath::Clamp(TargetClients, SharedCityCapacityMinClients, SharedCityCapacityMaxClients);
}

const TArray<FVector>& GetSundaleRouteWaypoints()
{
	static const TArray<FVector> Waypoints = {
		JobInteractionLocation,
		FVector(12500.0, 0.0, 0.0),
		FVector(12500.0, 9000.0, 0.0),
		FVector(12500.0, 18000.0, 0.0),
		StadiumEntranceThreshold,
		SportsbookInteractionLocation,
		FVector(-9500.0, 18000.0, 0.0),
		FVector(-9500.0, 16000.0, 0.0),
		FVector(-9500.0, 5000.0, 0.0),
		FVector(-9500.0, 0.0, 0.0),
		FVector::ZeroVector,
	};
	return Waypoints;
}

const TArray<FString>& GetSundaleRouteWaypointLabels()
{
	static const TArray<FString> Labels = {
		TEXT("Job"), TEXT("SoutheastCorner"), TEXT("Clothing"), TEXT("NortheastCorner"),
		TEXT("Arena"), TEXT("Sportsbook"), TEXT("NorthwestCorner"), TEXT("Court"),
		TEXT("Furniture"), TEXT("SouthwestCorner"), TEXT("Studio"),
	};
	return Labels;
}

const FKey KeyForward = EKeys::W;
const FKey KeyBackward = EKeys::S;
const FKey KeyLeft = EKeys::A;
const FKey KeyRight = EKeys::D;
const FKey KeyMouseYaw = EKeys::MouseX;
const FKey KeyMousePitch = EKeys::MouseY;
const FKey KeyRun = EKeys::LeftShift;
const FKey KeyJump = EKeys::SpaceBar;
const FKey KeyInteract = EKeys::E;
const FKey KeyLeagueView = EKeys::L;
const FKey KeyLeaguePrevious = EKeys::Comma;
const FKey KeyLeagueNext = EKeys::Period;
const FKey KeyStakeDecrease = EKeys::Hyphen;
const FKey KeyStakeIncrease = EKeys::Equals;
const FKey KeyConfirm = EKeys::Enter;
const FKey KeyMarketPrevious = EKeys::Left;
const FKey KeyMarketNext = EKeys::Right;
const FKey KeyMenuClose = EKeys::Escape;
const FKey KeyControllerMoveX = EKeys::Gamepad_LeftX;
const FKey KeyControllerMoveY = EKeys::Gamepad_LeftY;
const FKey KeyControllerLookX = EKeys::Gamepad_RightX;
const FKey KeyControllerLookY = EKeys::Gamepad_RightY;
const FKey KeyControllerRun = EKeys::Gamepad_LeftThumbstick;
const FKey KeyControllerJump = EKeys::Gamepad_FaceButton_Bottom;
const FKey KeyControllerMarketPrevious = EKeys::Gamepad_LeftShoulder;
const FKey KeyControllerMarketNext = EKeys::Gamepad_RightShoulder;
const FKey KeyControllerMenuClose = EKeys::Gamepad_FaceButton_Right;
const FKey KeyControllerTeamPrevious = EKeys::Gamepad_DPad_Left;
const FKey KeyControllerTeamNext = EKeys::Gamepad_DPad_Right;
const FKey KeyControllerStakeDecrease = EKeys::Gamepad_DPad_Down;
const FKey KeyControllerStakeIncrease = EKeys::Gamepad_DPad_Up;
const FName TicketBoothHomeTeamHitBox(TEXT("TicketBoothTeam0"));
const FName TicketBoothAwayTeamHitBox(TEXT("TicketBoothTeam1"));
const FName TicketBoothStakeDecreaseHitBox(TEXT("TicketBoothStakeDecrease"));
const FName TicketBoothStakeIncreaseHitBox(TEXT("TicketBoothStakeIncrease"));
const FName TicketBoothConfirmHitBox(TEXT("TicketBoothConfirm"));
}

bool FOddsWellStarterOutfitState::Equip(const FName ItemId, const EOddsWellStarterEquipmentSlot Slot, FString& OutError)
{
	EOddsWellStarterEquipmentSlot ResolvedSlot = EOddsWellStarterEquipmentSlot::Top;
	if (!ResolveOddsWellStarterEquipmentSlot(ItemId, ResolvedSlot, OutError))
	{
		return false;
	}
	if (ResolvedSlot != Slot)
	{
		OutError = FString::Printf(TEXT("Starter equipment %s does not belong in the requested slot."), *ItemId.ToString());
		return false;
	}
	FName& Equipped = Slot == EOddsWellStarterEquipmentSlot::Top ? EquippedTop : EquippedBottom;
	if (!Equipped.IsNone())
	{
		OutError = TEXT("The requested starter equipment slot is already occupied.");
		return false;
	}
	Equipped = ItemId;
	OutError.Reset();
	return true;
}

bool FOddsWellStarterOutfitState::Unequip(const EOddsWellStarterEquipmentSlot Slot, FString& OutError)
{
	FName& Equipped = Slot == EOddsWellStarterEquipmentSlot::Top ? EquippedTop : EquippedBottom;
	if (Equipped.IsNone())
	{
		OutError = TEXT("The requested starter equipment slot is already empty.");
		return false;
	}
	Equipped = NAME_None;
	OutError.Reset();
	return true;
}

bool FOddsWellStarterOutfitState::ValidateComplete(FString& OutError) const
{
	FName TopId;
	FName BottomId;
	if (!GetOddsWellStarterEquipmentIds(TopId, BottomId, OutError))
	{
		return false;
	}
	if (EquippedTop != TopId || EquippedBottom != BottomId)
	{
		OutError = TEXT("The starter outfit requires one valid top and one valid bottom.");
		return false;
	}
	OutError.Reset();
	return true;
}

FName FOddsWellStarterOutfitState::GetEquipped(const EOddsWellStarterEquipmentSlot Slot) const
{
	return Slot == EOddsWellStarterEquipmentSlot::Top ? EquippedTop : EquippedBottom;
}

void FOddsWellStarterOutfitState::Reset()
{
	EquippedTop = NAME_None;
	EquippedBottom = NAME_None;
}

AOddsWellPlaceholderCharacter::AOddsWellPlaceholderCharacter()
{
	PrimaryActorTick.bCanEverTick = true;
	bReplicates = true;
	SetReplicateMovement(true);
	GetCapsuleComponent()->InitCapsuleSize(CapsuleRadius, CapsuleHalfHeight);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Pawn, SharedCityPlayerCollision);
	GetMesh()->SetHiddenInGame(true);
	GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	PrimitiveBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NeutralPrimitiveBody"));
	PrimitiveBody->SetupAttachment(GetCapsuleComponent());
	PrimitiveBody->SetStaticMesh(Cylinder);
	PrimitiveBody->SetRelativeLocation(FVector(0.0, 0.0, -20.0));
	PrimitiveBody->SetRelativeScale3D(FVector(0.46, 0.46, 1.28));
	PrimitiveBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	PrimitiveHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NeutralPrimitiveHead"));
	PrimitiveHead->SetupAttachment(GetCapsuleComponent());
	PrimitiveHead->SetStaticMesh(Cube);
	PrimitiveHead->SetRelativeLocation(FVector(0.0, 0.0, 65.0));
	PrimitiveHead->SetRelativeScale3D(FVector(0.55));
	PrimitiveHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	StarterOutfitTop = CreateDefaultSubobject<UStaticMeshComponent>(TopComponentName);
	StarterOutfitTop->SetupAttachment(GetCapsuleComponent());
	StarterOutfitTop->SetStaticMesh(Cube);
	StarterOutfitTop->SetRelativeLocation(FVector(0.0, 0.0, 5.0));
	StarterOutfitTop->SetRelativeScale3D(FVector(0.62, 0.50, 0.50));
	StarterOutfitTop->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	StarterOutfitTop->SetVisibility(false);

	StarterOutfitBottom = CreateDefaultSubobject<UStaticMeshComponent>(BottomComponentName);
	StarterOutfitBottom->SetupAttachment(GetCapsuleComponent());
	StarterOutfitBottom->SetStaticMesh(Cube);
	StarterOutfitBottom->SetRelativeLocation(FVector(0.0, 0.0, -52.0));
	StarterOutfitBottom->SetRelativeScale3D(FVector(0.56, 0.46, 0.48));
	StarterOutfitBottom->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	StarterOutfitBottom->SetVisibility(false);

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("ThirdPersonCameraBoom"));
	CameraBoom->SetupAttachment(GetCapsuleComponent());
	CameraBoom->SetRelativeLocation(FVector(0.0, 0.0, 65.0));
	CameraBoom->TargetArmLength = CameraDistance;
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bDoCollisionTest = UseCameraCollision;
	CameraBoom->ProbeChannel = ECC_Camera;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ThirdPersonFollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	SharedCityNameplate = CreateDefaultSubobject<UTextRenderComponent>(TEXT("SharedCityNameplate"));
	SharedCityNameplate->SetupAttachment(GetCapsuleComponent());
	SharedCityNameplate->SetRelativeLocation(FVector(0.0, 0.0, 135.0));
	SharedCityNameplate->SetHorizontalAlignment(EHTA_Center);
	SharedCityNameplate->SetTextRenderColor(FColor::White);
	SharedCityNameplate->SetWorldSize(24.0f);
	SharedCityNameplate->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SharedCityNameplate->SetVisibility(false);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.0f, 500.0f, 0.0f);
	Movement->MaxWalkSpeed = WalkSpeed;
	Movement->JumpZVelocity = JumpVelocity;
	Movement->AirControl = 0.2f;
	Movement->NavAgentProps.bCanJump = true;
	Movement->NavAgentProps.bCanCrouch = AllowCrouch;
	Movement->NavAgentProps.bCanFly = AllowFlight;
	Movement->NavAgentProps.bCanSwim = AllowSwimming;
}

void AOddsWellPlaceholderCharacter::BeginPlay()
{
	Super::BeginPlay();
	bQaEnabled = FParse::Param(FCommandLine::Get(), TEXT("LocomotionQa"));
	bQaAutoExit = FParse::Param(FCommandLine::Get(), TEXT("LocomotionAutoExit"));
	bOutfitQaEnabled = FParse::Param(FCommandLine::Get(), TEXT("OutfitQa"));
	bAppearanceQa = UseOddsWellAppearanceQaSlot();
	bAppearanceQaCleanup = FParse::Param(FCommandLine::Get(), TEXT("AppearanceQaCleanup"));
	bSundaleRouteQa = FParse::Param(FCommandLine::Get(), TEXT("SundaleRouteQa"));
	bSundaleRouteRun = FParse::Param(FCommandLine::Get(), TEXT("SundaleRouteRun"));
	bSharedCityQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityQa"));
	bSharedCityCapacityQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityCapacityQa"));
	bStudioPersistenceQa = FParse::Param(FCommandLine::Get(), TEXT("StudioPersistenceQa"));
	bStudioPersistenceQaVerify = FParse::Param(FCommandLine::Get(), TEXT("StudioPersistenceQaVerify"));
	bStudioQa = FParse::Param(FCommandLine::Get(), TEXT("StudioQa")) || bStudioPersistenceQa || bStudioPersistenceQaVerify;
	bCameraOrbitQa = FParse::Param(FCommandLine::Get(), TEXT("CameraOrbitQa"));
	bPublicLeagueQa = FParse::Param(FCommandLine::Get(), TEXT("PublicLeagueQa"));
	bStadiumQa = FParse::Param(FCommandLine::Get(), TEXT("StadiumQa"));
	bCanonicalPendingReceiptQa =
		FParse::Param(FCommandLine::Get(), TEXT("CanonicalPendingReceiptQa"));
	bCanonicalPostLockQa =
		FParse::Param(FCommandLine::Get(), TEXT("CanonicalPostLockQa"));
	bCanonicalSettledLossReceiptQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalSettledLossReceiptQa"));
	bCanonicalBetSlipReviewQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalBetSlipReviewQa"));
	bCanonicalHarborFortyPlacementQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalHarborFortyPlacementQa"));
	bCanonicalMesaFortyPlacementQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMesaFortyPlacementQa"));
	bCanonicalAutomaticTipoffLockQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQa"))
		|| FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQaVerify"));
	bCanonicalAutomaticTipoffLockQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQaVerify"));
	bCanonicalHarborFortyPlacementQa =
		bCanonicalHarborFortyPlacementQa
		|| bCanonicalAutomaticTipoffLockQa;
	bCanonicalMissingHeldOpenTipoffQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMissingHeldOpenTipoffQa"));
	bSportsbookOfferQa =
		FParse::Param(FCommandLine::Get(), TEXT("SportsbookOfferQa"))
		|| bCanonicalPendingReceiptQa
		|| bCanonicalPostLockQa
		|| bCanonicalSettledLossReceiptQa
		|| bCanonicalBetSlipReviewQa
		|| bCanonicalHarborFortyPlacementQa
		|| bCanonicalMesaFortyPlacementQa
		|| bCanonicalMissingHeldOpenTipoffQa;
	bSportsbookWagerQaVerify = FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQaVerify"));
	bSportsbookWagerQaMode = FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQa")) || bSportsbookWagerQaVerify;
	bSportsbookWagerQaAuto = FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQaAuto")) || bSportsbookWagerQaVerify;
	bSportsbookReceiptQaMode = FParse::Param(FCommandLine::Get(), TEXT("SportsbookReceiptQa"));
	bSportsbookReceiptQaAuto = FParse::Param(FCommandLine::Get(), TEXT("SportsbookReceiptQaAuto"));
	bJobPayoutQaVerify = FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQaVerify"));
	bJobRecoveryQa = FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQa"));
	bJobRecoveryQaVerify = FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQaVerify"));
	bJobQa = FParse::Param(FCommandLine::Get(), TEXT("JobQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQa"))
		|| bJobPayoutQaVerify
		|| bJobRecoveryQa
		|| bJobRecoveryQaVerify;
	SharedCityQaTargetClients = GetSharedCityQaTargetClients();
	if (GetNetMode() == NM_Standalone && GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>())
	{
		FOddsWellStudioHomeState Home;
		FString Error;
		bOwnsStudio = LoadOwnedOddsWellStudio(UseOddsWellStudioHomeQaSlot(), Home, Error) && Home.bOwnsStudio;
	}
	UMaterialInterface* BasicShapeMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (!BasicShapeMaterial)
	{
		ReportOutfitError(TEXT("The native starter outfit material could not be loaded."));
		bOutfitQaEnabled = false;
	}
	else
	{
		StarterOutfitMaterial = UMaterialInstanceDynamic::Create(BasicShapeMaterial, this);
		PrimitiveSkinMaterial = UMaterialInstanceDynamic::Create(BasicShapeMaterial, this);
		if (!StarterOutfitMaterial || !PrimitiveSkinMaterial)
		{
			ReportAppearanceError(TEXT("The native placeholder material instances could not be created."));
			bOutfitQaEnabled = false;
		}
		else
		{
			StarterOutfitMaterial->SetVectorParameterValue(TEXT("Color"), StarterOffWhite);
			StarterOutfitTop->SetMaterial(0, StarterOutfitMaterial);
			StarterOutfitBottom->SetMaterial(0, StarterOutfitMaterial);
			PrimitiveBody->SetMaterial(0, PrimitiveSkinMaterial);
			PrimitiveHead->SetMaterial(0, PrimitiveSkinMaterial);
		}
	}
	bool bAppearanceReady = true;
	if (GetNetMode() == NM_Standalone)
	{
		bAppearanceReady = ApplySavedOrFallbackAppearance();
	}
	else if (HasAuthority())
	{
		FOddsWellResolvedCharacterAppearance Fallback;
		FString Source;
		FString Error;
		bAppearanceReady = ResolveOddsWellCharacterAppearance(nullptr, false, Fallback, Source, Error);
		if (bAppearanceReady && Fallback.Preset)
		{
			SetAuthoritativeSharedCityAppearance(Fallback.Preset->Id, Fallback.TopItemId, Fallback.BottomItemId, false, TEXT("server_fallback"));
		}
	}
	else if (!SharedCityAppearance.PresetId.IsNone())
	{
		bAppearanceReady = ApplySharedCityAppearance(TEXT("replicated_initial"));
	}
	if (GetNetMode() == NM_ListenServer && IsLocallyControlled())
	{
		SubmitLocalSharedCityAppearance();
	}
	if (!bAppearanceReady)
	{
		bOutfitQaEnabled = false;
	}
	SyncSharedCityNameplate();
	if (IsLocallyControlled())
	{
		PublicLeagueSnapshot = MakeUnique<FOddsWellPublicLeagueSnapshot>();
		FString Error;
		if (!LoadOddsWellPublicLeagueSnapshot(*PublicLeagueSnapshot, Error))
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_PUBLIC_LEAGUE|result=FAIL|reason=%s"), *Error);
			PublicLeagueSnapshot.Reset();
		}
		else
		{
			int32 AthleteCount = 0;
			int32 UnavailableCount = 0;
			for (const FOddsWellPublicTeam& Team : PublicLeagueSnapshot->Teams)
			{
				AthleteCount += Team.Athletes.Num();
				for (const FOddsWellPublicAthlete& Athlete : Team.Athletes)
				{
					UnavailableCount += Athlete.bAvailable ? 0 : 1;
				}
			}
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_PUBLIC_LEAGUE|result=PASS|public_only=true|teams=%d|athletes=%d|standings=%d|games=%d|unavailable=%d|pages=%d"), PublicLeagueSnapshot->Teams.Num(), AthleteCount, PublicLeagueSnapshot->Standings.Num(), PublicLeagueSnapshot->Games.Num(), UnavailableCount, GetOddsWellPublicLeaguePageCount(*PublicLeagueSnapshot));
			if (bPublicLeagueQa)
			{
				bPublicLeagueVisible = true;
				PublicLeaguePage = GetOddsWellPublicLeaguePageCount(*PublicLeagueSnapshot) - 1;
				ShowLeaguePage();
				if (FParse::Param(FCommandLine::Get(), TEXT("PublicLeagueAutoExit")))
				{
					QaExitAt = FPlatformTime::Seconds() + 2.0;
				}
			}
		}
		RefreshSportsbookOfferPreview();
		if (bSportsbookReceiptQaMode)
		{
			SportsbookReceipt = MakeUnique<FOddsWellPendingQaMatchWinnerReceipt>();
			if (!LoadOddsWellPendingQaMatchWinnerReceipt(*SportsbookReceipt, Error))
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_RECEIPT|result=FAIL|closed=true|reason=%s"), *Error);
				SportsbookReceipt.Reset();
				bSportsbookReceiptQaAuto = false;
			}
			else
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Display,
					TEXT("ODDSWELL_SPORTSBOOK_RECEIPT|result=READY|cold_restore=true|read_only=true|request_api=false|request_id=%s|offer_id=%s|status=%s|ledger_sequence=%lld|ledger_delta=%lld|balance=%lld"),
					*SportsbookReceipt->RequestId,
					*SportsbookReceipt->OfferId,
					*SportsbookReceipt->Status.ToString(),
					SportsbookReceipt->LedgerSequence,
					SportsbookReceipt->LedgerDelta,
					SportsbookReceipt->CurrentBalance);
			}
		}
		if (bSportsbookWagerQaMode)
		{
			SportsbookQaOffer = MakeUnique<FOddsWellMatchWinnerOffer>();
			if (!BuildOddsWellUpcomingQaMatchWinnerOffer(*SportsbookQaOffer, Error))
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_WAGER|result=FAIL|reason=qa_offer_unavailable|detail=%s"), *Error);
				SportsbookQaOffer.Reset();
				bSportsbookWagerQaAuto = false;
			}
			else
			{
				SportsbookQaStake = SportsbookQaOffer->MinimumStake;
				UE_LOG(
					LogOddsWellLocomotion,
					Display,
					TEXT("ODDSWELL_SPORTSBOOK_WAGER|result=READY|qa=true|noncanonical=true|offer_id=%s|season=%d|game=%d|accepted_unix=%lld|lock_unix=%lld|accepted_before_lock=%s|result_state=false"),
					*SportsbookQaOffer->OfferId,
					SportsbookQaOffer->SeasonNumber,
					SportsbookQaOffer->GameNumber,
					GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
					SportsbookQaOffer->LockUnixSeconds,
					GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds() < SportsbookQaOffer->LockUnixSeconds ? TEXT("true") : TEXT("false"));
			}
		}
	}
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_LOCOMOTION_READY|spawn=%s|walk=%.0f|run=%.0f|jump=%.0f"), *SafeSpawnLocation.ToCompactString(), WalkSpeed, RunSpeed, JumpVelocity);
}

void AOddsWellPlaceholderCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(AOddsWellPlaceholderCharacter, SharedCityPlayerNumber);
	DOREPLIFETIME(AOddsWellPlaceholderCharacter, SharedCityAppearance);
}

void AOddsWellPlaceholderCharacter::AssignSharedCityPlayerNumber(const int32 PlayerNumber)
{
	if (!HasAuthority() || PlayerNumber < 1)
	{
		return;
	}
	SharedCityPlayerNumber = PlayerNumber;
	SyncSharedCityNameplate();
	ForceNetUpdate();
}

void AOddsWellPlaceholderCharacter::OnRep_SharedCityPlayerNumber()
{
	SyncSharedCityNameplate();
}

void AOddsWellPlaceholderCharacter::OnRep_SharedCityAppearance()
{
	if (PrimitiveSkinMaterial)
	{
		ApplySharedCityAppearance(TEXT("replicated"));
	}
}

bool AOddsWellPlaceholderCharacter::HasValidSharedCityAppearance() const
{
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Error;
	return ValidateOddsWellCharacterAppearanceIds(
		SharedCityAppearance.PresetId,
		SharedCityAppearance.TopItemId,
		SharedCityAppearance.BottomItemId,
		Appearance,
		Error);
}

void AOddsWellPlaceholderCharacter::SyncSharedCityNameplate()
{
	if (!SharedCityNameplate)
	{
		return;
	}
	SharedCityNameplate->SetText(FText::FromString(FString::Printf(TEXT("Player %d"), SharedCityPlayerNumber)));
	SharedCityNameplate->SetVisibility(SharedCityPlayerNumber > 0, true);
}

void AOddsWellPlaceholderCharacter::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);
	if (APlayerController* PlayerController = Cast<APlayerController>(NewController))
	{
		PlayerController->SetControlRotation(FRotator(-12.0f, 0.0f, 0.0f));
		if (PlayerController->PlayerCameraManager)
		{
			PlayerController->PlayerCameraManager->ViewPitchMin = CameraPitchMin;
			PlayerController->PlayerCameraManager->ViewPitchMax = CameraPitchMax;
		}
	}
}

void AOddsWellPlaceholderCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();
	if (GetNetMode() == NM_Client && IsLocallyControlled())
	{
		SubmitLocalSharedCityAppearance();
	}
}

void AOddsWellPlaceholderCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	PlayerInputComponent->BindAxisKey(KeyMouseYaw, this, &AOddsWellPlaceholderCharacter::LookYaw);
	PlayerInputComponent->BindAxisKey(KeyMousePitch, this, &AOddsWellPlaceholderCharacter::LookPitchMouse);
	PlayerInputComponent->BindKey(KeyRun, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartRun);
	PlayerInputComponent->BindKey(KeyRun, IE_Released, this, &AOddsWellPlaceholderCharacter::StopRun);
	PlayerInputComponent->BindKey(KeyJump, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartJump);
	PlayerInputComponent->BindKey(KeyJump, IE_Released, this, &AOddsWellPlaceholderCharacter::StopJump);
	PlayerInputComponent->BindKey(KeyLeagueView, IE_Pressed, this, &AOddsWellPlaceholderCharacter::ToggleLeagueView);
	PlayerInputComponent->BindKey(KeyLeaguePrevious, IE_Pressed, this, &AOddsWellPlaceholderCharacter::PreviousLeaguePage);
	PlayerInputComponent->BindKey(KeyLeagueNext, IE_Pressed, this, &AOddsWellPlaceholderCharacter::NextLeaguePage);
	PlayerInputComponent->BindKey(KeyLeaguePrevious, IE_Pressed, this, &AOddsWellPlaceholderCharacter::SelectPreviousSportsbookQaTeam);
	PlayerInputComponent->BindKey(KeyLeagueNext, IE_Pressed, this, &AOddsWellPlaceholderCharacter::SelectNextSportsbookQaTeam);
	PlayerInputComponent->BindKey(KeyStakeDecrease, IE_Pressed, this, &AOddsWellPlaceholderCharacter::DecreaseSportsbookQaStake);
	PlayerInputComponent->BindKey(KeyStakeIncrease, IE_Pressed, this, &AOddsWellPlaceholderCharacter::IncreaseSportsbookQaStake);
	PlayerInputComponent->BindKey(KeyLeaguePrevious, IE_Pressed, this, &AOddsWellPlaceholderCharacter::SelectPreviousTicketBoothReviewTeam);
	PlayerInputComponent->BindKey(KeyLeagueNext, IE_Pressed, this, &AOddsWellPlaceholderCharacter::SelectNextTicketBoothReviewTeam);
	PlayerInputComponent->BindKey(KeyStakeDecrease, IE_Pressed, this, &AOddsWellPlaceholderCharacter::DecreaseTicketBoothReviewStake);
	PlayerInputComponent->BindKey(KeyStakeIncrease, IE_Pressed, this, &AOddsWellPlaceholderCharacter::IncreaseTicketBoothReviewStake);
	PlayerInputComponent->BindKey(KeyConfirm, IE_Pressed, this, &AOddsWellPlaceholderCharacter::ConfirmSportsbookQaWager);
	PlayerInputComponent->BindKey(KeyConfirm, IE_Pressed, this, &AOddsWellPlaceholderCharacter::ConfirmTicketBoothWager);
	PlayerInputComponent->BindKey(KeyMarketPrevious, IE_Pressed, this, &AOddsWellPlaceholderCharacter::PreviousSportsbookMarketPage);
	PlayerInputComponent->BindKey(KeyMarketNext, IE_Pressed, this, &AOddsWellPlaceholderCharacter::NextSportsbookMarketPage);
	PlayerInputComponent->BindKey(KeyMenuClose, IE_Pressed, this, &AOddsWellPlaceholderCharacter::CloseTicketBoothMenu);

	PlayerInputComponent->BindAxisKey(KeyControllerMoveY, this, &AOddsWellPlaceholderCharacter::MoveForward);
	PlayerInputComponent->BindAxisKey(KeyControllerMoveX, this, &AOddsWellPlaceholderCharacter::MoveRight);
	PlayerInputComponent->BindAxisKey(KeyControllerLookX, this, &AOddsWellPlaceholderCharacter::LookYaw);
	PlayerInputComponent->BindAxisKey(KeyControllerLookY, this, &AOddsWellPlaceholderCharacter::LookPitchController);
	PlayerInputComponent->BindKey(KeyControllerRun, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartRun);
	PlayerInputComponent->BindKey(KeyControllerRun, IE_Released, this, &AOddsWellPlaceholderCharacter::StopRun);
	PlayerInputComponent->BindKey(KeyControllerJump, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartJump);
	PlayerInputComponent->BindKey(KeyControllerJump, IE_Released, this, &AOddsWellPlaceholderCharacter::StopJump);
	PlayerInputComponent->BindKey(KeyControllerJump, IE_Pressed, this, &AOddsWellPlaceholderCharacter::ConfirmTicketBoothWager);
	PlayerInputComponent->BindKey(KeyControllerMarketPrevious, IE_Pressed, this, &AOddsWellPlaceholderCharacter::PreviousSportsbookMarketPage);
	PlayerInputComponent->BindKey(KeyControllerMarketNext, IE_Pressed, this, &AOddsWellPlaceholderCharacter::NextSportsbookMarketPage);
	PlayerInputComponent->BindKey(KeyControllerMenuClose, IE_Pressed, this, &AOddsWellPlaceholderCharacter::CloseTicketBoothMenu);
	PlayerInputComponent->BindKey(KeyControllerTeamPrevious, IE_Pressed, this, &AOddsWellPlaceholderCharacter::SelectPreviousTicketBoothReviewTeam);
	PlayerInputComponent->BindKey(KeyControllerTeamNext, IE_Pressed, this, &AOddsWellPlaceholderCharacter::SelectNextTicketBoothReviewTeam);
	PlayerInputComponent->BindKey(KeyControllerStakeDecrease, IE_Pressed, this, &AOddsWellPlaceholderCharacter::DecreaseTicketBoothReviewStake);
	PlayerInputComponent->BindKey(KeyControllerStakeIncrease, IE_Pressed, this, &AOddsWellPlaceholderCharacter::IncreaseTicketBoothReviewStake);
}

void AOddsWellPlaceholderCharacter::ToggleLeagueView()
{
	if (!IsLocallyControlled() || !PublicLeagueSnapshot)
	{
		return;
	}
	if (!bPublicLeagueVisible && bSportsbookOfferVisible)
	{
		CloseTicketBoothMenu();
	}
	bPublicLeagueVisible = !bPublicLeagueVisible;
	ShowLeaguePage();
}

void AOddsWellPlaceholderCharacter::PreviousLeaguePage()
{
	if (!bPublicLeagueVisible || !PublicLeagueSnapshot)
	{
		return;
	}
	const int32 PageCount = GetOddsWellPublicLeaguePageCount(*PublicLeagueSnapshot);
	PublicLeaguePage = (PublicLeaguePage - 1 + PageCount) % PageCount;
	ShowLeaguePage();
}

void AOddsWellPlaceholderCharacter::NextLeaguePage()
{
	if (!bPublicLeagueVisible || !PublicLeagueSnapshot)
	{
		return;
	}
	PublicLeaguePage = (PublicLeaguePage + 1) % GetOddsWellPublicLeaguePageCount(*PublicLeagueSnapshot);
	ShowLeaguePage();
}

void AOddsWellPlaceholderCharacter::ShowLeaguePage()
{
	if (!GEngine)
	{
		return;
	}
	GEngine->RemoveOnScreenDebugMessage(912013);
	if (bPublicLeagueVisible && PublicLeagueSnapshot)
	{
		GEngine->AddOnScreenDebugMessage(912013, 3600.0f, FColor::White, BuildOddsWellPublicLeaguePage(*PublicLeagueSnapshot, PublicLeaguePage));
	}
}

void AOddsWellPlaceholderCharacter::RefreshSportsbookOfferPreview()
{
	TicketBoothReviewSelectionIndex = INDEX_NONE;
	TicketBoothReviewStake = 10;
	bTicketBoothWagerArmed = false;
	bTicketBoothWagerSubmitting = false;
	SportsbookSettledLossReceipt =
		MakeUnique<FOddsWellCanonicalSettledLossReceipt>();
	FString Error;
	const EOddsWellCanonicalSettledLossReceiptResult SettledResult =
		LoadOddsWellCanonicalSettledLossReceipt(
			*SportsbookSettledLossReceipt,
			Error);
	if (SettledResult == EOddsWellCanonicalSettledLossReceiptResult::Rejected)
	{
		SportsbookSettledLossReceipt.Reset();
		SportsbookCanonicalReceipt.Reset();
		SportsbookOfferPreview.Reset();
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_SETTLED_LOSS_RECEIPT|result=REJECTED|unavailable=true|partial=false|teams=false|score=false|return=false|balance=false|archive_fallback=false|projection=false|write=false"));
		return;
	}
	if (SettledResult == EOddsWellCanonicalSettledLossReceiptResult::Ready)
	{
		SportsbookCanonicalReceipt.Reset();
		SportsbookOfferPreview.Reset();
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_SETTLED_LOSS_RECEIPT|result=READY|read_only=true|selected_team=Harbor_City_Waves|stake=%lld|final_score=%d-%d|winner=Mesa_Vista_Sol|returned=%lld|net=%lld|balance=%lld|ledger_entries=%d|ids_visible=false|hashes_visible=false|projection=false|write=false"),
			SportsbookSettledLossReceipt->Stake,
			SportsbookSettledLossReceipt->HomeScore,
			SportsbookSettledLossReceipt->AwayScore,
			SportsbookSettledLossReceipt->Returned,
			SportsbookSettledLossReceipt->Net,
			SportsbookSettledLossReceipt->CurrentBalance,
			SportsbookSettledLossReceipt->LedgerEntryCount);
		return;
	}
	SportsbookSettledLossReceipt.Reset();
	SportsbookCanonicalReceipt =
		MakeUnique<FOddsWellCanonicalPendingMatchWinnerReceipt>();
	const EOddsWellCanonicalPendingReceiptResult ReceiptResult =
		LoadOddsWellCanonicalPendingMatchWinnerReceipt(
			*SportsbookCanonicalReceipt,
			Error);
	if (ReceiptResult == EOddsWellCanonicalPendingReceiptResult::Rejected)
	{
		SportsbookCanonicalReceipt.Reset();
		SportsbookOfferPreview.Reset();
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_PENDING_RECEIPT|result=REJECTED|closed=true|partial=false|migration=false|write=false|request_api=false|locked_claim=false|settled_claim=false"));
		return;
	}
	if (ReceiptResult == EOddsWellCanonicalPendingReceiptResult::Missing)
	{
		SportsbookCanonicalReceipt.Reset();
	}

	SportsbookOfferPreview = MakeUnique<FOddsWellMatchWinnerOfferPreview>();
	if (!LoadOddsWellCanonicalMatchWinnerOfferPreview(*SportsbookOfferPreview, Error))
	{
		SportsbookCanonicalReceipt.Reset();
		SportsbookOfferPreview.Reset();
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_TICKET_BOOTH|result=UNAVAILABLE|locked_or_invalid=true|teams=false|prices=false|archive_fallback=false|submission=false|debit=false"));
		return;
	}
	if (SportsbookCanonicalReceipt)
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_PENDING_RECEIPT|result=READY|cold_restore=true|read_only=true|canonical=true|selected_team=%s|probability_e8=%lld|odds_e4=%lld|stake=%lld|gross_return=%lld|balance=%lld|accepted_unix=%lld|tipoff_unix=%lld|status=%s|partial=false|migration=false|write=false|request_api=false|debit=false|locked_claim=false|settled_claim=false"),
			*SportsbookCanonicalReceipt->SelectedTeam,
			SportsbookCanonicalReceipt->SelectedWinProbabilityE8,
			SportsbookCanonicalReceipt->SelectedDecimalOddsE4,
			SportsbookCanonicalReceipt->Stake,
			SportsbookCanonicalReceipt->GrossReturn,
			SportsbookCanonicalReceipt->CurrentBalance,
			SportsbookCanonicalReceipt->AcceptedUnixSeconds,
			SportsbookCanonicalReceipt->LockUnixSeconds,
			*SportsbookCanonicalReceipt->Status.ToString());
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_TICKET_BOOTH|result=PASS|read_only=true|season=%d|game=%d|offer_id=%s|source=%s|selections=%d|minimum_stake=%lld|maximum_stake=%lld|increment=%lld|lock_unix=%lld|timing_authority=server|environment=local_beta|archive_fallback=false|submission=false|debit=false"),
		SportsbookOfferPreview->SeasonNumber,
		SportsbookOfferPreview->GameNumber,
		*SportsbookOfferPreview->OfferId,
		*SportsbookOfferPreview->SourceModel,
		SportsbookOfferPreview->Selections.Num(),
		SportsbookOfferPreview->MinimumStake,
		SportsbookOfferPreview->MaximumStake,
		SportsbookOfferPreview->StakeIncrement,
		SportsbookOfferPreview->LockUnix);
	ResetTicketBoothReview();
}

void AOddsWellPlaceholderCharacter::ToggleSportsbookOfferPreview()
{
	const bool bAtSportsbook = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), SportsbookInteractionLocation) <= SportsbookInteractionRadius;
	if (!IsLocallyControlled() || !bAtSportsbook)
	{
		return;
	}
	if (!bSportsbookOfferVisible && bPublicLeagueVisible)
	{
		bPublicLeagueVisible = false;
		ShowLeaguePage();
	}
	bSportsbookOfferVisible = !bSportsbookOfferVisible;
	if (bSportsbookOfferVisible)
	{
		RefreshSportsbookOfferPreview();
		SportsbookMarketPage = 0;
	}
	SetTicketBoothInputMode(bSportsbookOfferVisible);
	ShowSportsbookOfferPreview();
}

void AOddsWellPlaceholderCharacter::ShowSportsbookOfferPreview()
{
	if (!GEngine)
	{
		return;
	}
	GEngine->RemoveOnScreenDebugMessage(912017);
}

bool AOddsWellPlaceholderCharacter::IsTicketBoothPromptVisible() const
{
	return bAtSportsbookInteraction
		&& !bSportsbookOfferVisible
		&& !bSportsbookWagerQaMode
		&& !bSportsbookReceiptQaMode;
}

void AOddsWellPlaceholderCharacter::SetTicketBoothMarketPage(const int32 Page)
{
	if (!IsTicketBoothMenuVisible())
	{
		return;
	}
	SportsbookMarketPage = (Page % TicketBoothMarketPageCount + TicketBoothMarketPageCount) % TicketBoothMarketPageCount;
	bTicketBoothWagerArmed = false;
}

void AOddsWellPlaceholderCharacter::PreviousSportsbookMarketPage()
{
	SetTicketBoothMarketPage(SportsbookMarketPage - 1);
}

void AOddsWellPlaceholderCharacter::NextSportsbookMarketPage()
{
	SetTicketBoothMarketPage(SportsbookMarketPage + 1);
}

bool AOddsWellPlaceholderCharacter::CanReviewTicketBoothBetSlip() const
{
	return bSportsbookOfferVisible
		&& SportsbookOfferPreview
		&& IsCanonicalBetSlipOfferUsable(*SportsbookOfferPreview)
		&& ShouldShowCanonicalBetSlipReview(
			true,
			SportsbookCanonicalReceipt != nullptr,
			SportsbookSettledLossReceipt != nullptr);
}

int64 AOddsWellPlaceholderCharacter::GetTicketBoothReviewGrossReturn() const
{
	if (!CanReviewTicketBoothBetSlip()
		|| !SportsbookOfferPreview->Selections.IsValidIndex(
			TicketBoothReviewSelectionIndex))
	{
		return 0;
	}
	return CalculateCanonicalBetSlipGrossReturn(
		TicketBoothReviewStake,
		SportsbookOfferPreview->Selections[TicketBoothReviewSelectionIndex]
			.WinProbabilityE8);
}

int64 AOddsWellPlaceholderCharacter::GetTicketBoothCurrentBalance() const
{
	const AOddsWellLocomotionGameMode* GameMode =
		GetWorld() ? GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>() : nullptr;
	return GameMode ? GameMode->GetOddsBucksBalance() : 0;
}

FString AOddsWellPlaceholderCharacter::GetTicketBoothReviewText() const
{
	return CanReviewTicketBoothBetSlip()
		? BuildCanonicalBetSlipReviewText(
			*SportsbookOfferPreview,
			TicketBoothReviewSelectionIndex,
			TicketBoothReviewStake,
			GetTicketBoothCurrentBalance())
		: FString(TEXT("BET SLIP UNAVAILABLE"));
}

bool AOddsWellPlaceholderCharacter::CanPlaceTicketBoothCanonicalForty() const
{
	return CanReviewTicketBoothBetSlip()
		&& SportsbookMarketPage == 0
		&& !bTicketBoothWagerSubmitting
		&& IsCanonicalFortyPlacementEligible(
			*SportsbookOfferPreview,
			TicketBoothReviewSelectionIndex,
			TicketBoothReviewStake,
			GetTicketBoothCurrentBalance());
}

void AOddsWellPlaceholderCharacter::SelectTicketBoothReviewTeam(
	const int32 SelectionIndex)
{
	if (CanReviewTicketBoothBetSlip()
		&& SportsbookMarketPage == 0
		&& SportsbookOfferPreview->Selections.IsValidIndex(SelectionIndex))
	{
		TicketBoothReviewSelectionIndex = SelectionIndex;
		bTicketBoothWagerArmed = false;
	}
}

void AOddsWellPlaceholderCharacter::SelectPreviousTicketBoothReviewTeam()
{
	if (!CanReviewTicketBoothBetSlip() || SportsbookMarketPage != 0)
	{
		return;
	}
	SelectTicketBoothReviewTeam(
		TicketBoothReviewSelectionIndex == INDEX_NONE
			? SportsbookOfferPreview->Selections.Num() - 1
			: (TicketBoothReviewSelectionIndex - 1
				+ SportsbookOfferPreview->Selections.Num())
				% SportsbookOfferPreview->Selections.Num());
}

void AOddsWellPlaceholderCharacter::SelectNextTicketBoothReviewTeam()
{
	if (!CanReviewTicketBoothBetSlip() || SportsbookMarketPage != 0)
	{
		return;
	}
	SelectTicketBoothReviewTeam(
		TicketBoothReviewSelectionIndex == INDEX_NONE
			? 0
			: (TicketBoothReviewSelectionIndex + 1)
				% SportsbookOfferPreview->Selections.Num());
}

void AOddsWellPlaceholderCharacter::DecreaseTicketBoothReviewStake()
{
	if (CanReviewTicketBoothBetSlip())
	{
		TicketBoothReviewStake = FMath::Max(
			SportsbookOfferPreview->MinimumStake,
			TicketBoothReviewStake - SportsbookOfferPreview->StakeIncrement);
		bTicketBoothWagerArmed = false;
	}
}

void AOddsWellPlaceholderCharacter::IncreaseTicketBoothReviewStake()
{
	if (CanReviewTicketBoothBetSlip())
	{
		TicketBoothReviewStake = FMath::Min(
			SportsbookOfferPreview->MaximumStake,
			TicketBoothReviewStake + SportsbookOfferPreview->StakeIncrement);
		bTicketBoothWagerArmed = false;
	}
}

void AOddsWellPlaceholderCharacter::ConfirmTicketBoothWager()
{
	if (!AdvanceCanonicalFortyConfirmation(
			CanPlaceTicketBoothCanonicalForty(),
			bTicketBoothWagerArmed))
	{
		return;
	}
	bTicketBoothWagerSubmitting = true;
	ServerPlaceCanonicalFortyWager(
		SportsbookOfferPreview
			&& SportsbookOfferPreview->Selections.IsValidIndex(
				TicketBoothReviewSelectionIndex)
			&& SportsbookOfferPreview->Selections[
				TicketBoothReviewSelectionIndex].Team
				== TEXT("Mesa Vista Sol"));
}

void AOddsWellPlaceholderCharacter::ResetTicketBoothReview()
{
	TicketBoothReviewSelectionIndex = INDEX_NONE;
	TicketBoothReviewStake = SportsbookOfferPreview
		&& IsCanonicalBetSlipOfferUsable(*SportsbookOfferPreview)
		? SportsbookOfferPreview->MinimumStake
		: 10;
	bTicketBoothWagerArmed = false;
	bTicketBoothWagerSubmitting = false;
}

void AOddsWellPlaceholderCharacter::CloseTicketBoothMenu()
{
	if (!bSportsbookOfferVisible)
	{
		return;
	}
	bSportsbookOfferVisible = false;
	ResetTicketBoothReview();
	SetTicketBoothInputMode(false);
	ShowSportsbookOfferPreview();
}

void AOddsWellPlaceholderCharacter::RefreshTicketBoothAfterCanonicalLock()
{
	if (IsLocallyControlled() && bSportsbookOfferVisible)
	{
		RefreshSportsbookOfferPreview();
		ShowSportsbookOfferPreview();
	}
}

void AOddsWellPlaceholderCharacter::SetTicketBoothInputMode(const bool bMenuOpen)
{
	APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController || !IsLocallyControlled())
	{
		return;
	}
	PlayerController->SetIgnoreMoveInput(bMenuOpen);
	PlayerController->SetIgnoreLookInput(bMenuOpen);
	PlayerController->bShowMouseCursor = bMenuOpen;
	PlayerController->bEnableClickEvents = bMenuOpen;
	if (bMenuOpen)
	{
		FInputModeGameAndUI InputMode;
		InputMode.SetHideCursorDuringCapture(false);
		PlayerController->SetInputMode(InputMode);
	}
	else
	{
		PlayerController->SetInputMode(FInputModeGameOnly());
	}
}

void AOddsWellPlaceholderCharacter::ToggleSportsbookQaWager()
{
	const bool bAtSportsbook = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), SportsbookInteractionLocation) <= SportsbookInteractionRadius;
	if (!IsLocallyControlled() || !SportsbookQaOffer || !bAtSportsbook)
	{
		return;
	}
	if (!bSportsbookQaWagerVisible && bPublicLeagueVisible)
	{
		bPublicLeagueVisible = false;
		ShowLeaguePage();
	}
	bSportsbookQaWagerVisible = !bSportsbookQaWagerVisible;
	if (!bSportsbookQaWagerVisible)
	{
		bSportsbookQaReviewing = false;
	}
	ShowSportsbookQaWager();
}

FString AOddsWellPlaceholderCharacter::BuildSportsbookQaWagerText() const
{
	if (!SportsbookQaOffer || !SportsbookQaOffer->Selections.IsValidIndex(SportsbookQaSelectionIndex))
	{
		return TEXT("QA MATCH WINNER REQUEST UNAVAILABLE");
	}
	const FOddsWellMatchWinnerSelection& Selection = SportsbookQaOffer->Selections[SportsbookQaSelectionIndex];
	const int64 GrossReturn = SportsbookQaStake * 100000000 / Selection.WinProbabilityE8;
	if (bSportsbookQaAccepted)
	{
		return FString::Printf(
			TEXT("QA MATCH WINNER REQUEST - ACCEPTED%s\n\nREQUEST ID\n%s\n\nSELECTED TEAM\n%s\n\nSTAKE\n%lld Odds Bucks\n\nRESULTING BALANCE\n%lld Odds Bucks\n\nSTATUS\naccepted_pending_lock\n\nNo score, winner, replay, result, lock, or settlement was created."),
			bSportsbookQaDuplicate ? TEXT(" (EXACT RETRY)") : TEXT(""),
			*SportsbookQaAcceptedRequestId,
			*SportsbookQaAcceptedTeam,
			SportsbookQaStake,
			SportsbookQaResultingBalance);
	}
	return FString::Printf(
		TEXT("QA ONLY - UPCOMING MATCH WINNER\nNONCANONICAL / MACHINE-LOCAL\n\n%s  vs  %s\n\nTEAM  <  %s  >     [, / .]\nSTAKE  -  %lld  +     [- / =]\n\nEXACT GROSS RETURN\n%lld Odds Bucks\n\n%s\n\nOffer %s\nAccepted %lld  |  Lock %lld"),
		*SportsbookQaOffer->HomeTeam,
		*SportsbookQaOffer->AwayTeam,
		*Selection.Team,
		SportsbookQaStake,
		GrossReturn,
		bSportsbookQaReviewing
			? TEXT("REVIEW THIS EXACT REQUEST\nPRESS ENTER AGAIN TO CONFIRM")
			: TEXT("PRESS ENTER TO REVIEW"),
		*SportsbookQaOffer->OfferId,
		GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
		SportsbookQaOffer->LockUnixSeconds);
}

void AOddsWellPlaceholderCharacter::ShowSportsbookQaWager()
{
	if (!GEngine)
	{
		return;
	}
	GEngine->RemoveOnScreenDebugMessage(912019);
	if (bSportsbookQaWagerVisible)
	{
		GEngine->AddOnScreenDebugMessage(912019, 3600.0f, bSportsbookQaAccepted ? FColor::Green : FColor::Yellow, BuildSportsbookQaWagerText());
	}
}

void AOddsWellPlaceholderCharacter::ToggleSportsbookReceipt()
{
	const bool bAtSportsbook = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), SportsbookInteractionLocation) <= SportsbookInteractionRadius;
	if (!IsLocallyControlled() || !SportsbookReceipt || !bAtSportsbook)
	{
		return;
	}
	if (!bSportsbookReceiptVisible && bPublicLeagueVisible)
	{
		bPublicLeagueVisible = false;
		ShowLeaguePage();
	}
	bSportsbookReceiptVisible = !bSportsbookReceiptVisible;
	ShowSportsbookReceipt();
}

FString AOddsWellPlaceholderCharacter::BuildSportsbookReceiptText() const
{
	if (!SportsbookReceipt)
	{
		return TEXT("PENDING MATCH WINNER RECEIPT UNAVAILABLE");
	}
	return FString::Printf(
		TEXT("QA MATCH WINNER RECEIPT - READ ONLY\nCOLD-RESTORED PERSISTED EVIDENCE\n\nREQUEST ID\n%s\n\nOFFER\n%s\nVERSION  %s\n\nSELECTED TEAM\n%s\n\nSTAKE\n%lld Odds Bucks\n\nACCEPTED  %lld\nLOCK  %lld\nSTATUS  %s\n\nLINKED LEDGER ENTRY\nSEQUENCE  %lld   DELTA  %lld\nREASON  %s\n\nCURRENT BALANCE\n%lld Odds Bucks\n\nNo request API, debit, lock, result, or mutation ran in this process."),
		*SportsbookReceipt->RequestId,
		*SportsbookReceipt->OfferId,
		*SportsbookReceipt->OfferVersion,
		*SportsbookReceipt->SelectedTeam,
		SportsbookReceipt->Stake,
		SportsbookReceipt->AcceptedUnixSeconds,
		SportsbookReceipt->LockUnixSeconds,
		*SportsbookReceipt->Status.ToString(),
		SportsbookReceipt->LedgerSequence,
		SportsbookReceipt->LedgerDelta,
		*SportsbookReceipt->LedgerReason.ToString(),
		SportsbookReceipt->CurrentBalance);
}

void AOddsWellPlaceholderCharacter::ShowSportsbookReceipt()
{
	if (!GEngine)
	{
		return;
	}
	GEngine->RemoveOnScreenDebugMessage(912021);
	if (bSportsbookReceiptVisible)
	{
		GEngine->AddOnScreenDebugMessage(912021, 3600.0f, FColor::Green, BuildSportsbookReceiptText());
	}
}

void AOddsWellPlaceholderCharacter::SelectPreviousSportsbookQaTeam()
{
	if (!bSportsbookQaWagerVisible || bSportsbookQaAccepted || !SportsbookQaOffer)
	{
		return;
	}
	SportsbookQaSelectionIndex = (SportsbookQaSelectionIndex - 1 + SportsbookQaOffer->Selections.Num()) % SportsbookQaOffer->Selections.Num();
	bSportsbookQaReviewing = false;
	ShowSportsbookQaWager();
}

void AOddsWellPlaceholderCharacter::SelectNextSportsbookQaTeam()
{
	if (!bSportsbookQaWagerVisible || bSportsbookQaAccepted || !SportsbookQaOffer)
	{
		return;
	}
	SportsbookQaSelectionIndex = (SportsbookQaSelectionIndex + 1) % SportsbookQaOffer->Selections.Num();
	bSportsbookQaReviewing = false;
	ShowSportsbookQaWager();
}

void AOddsWellPlaceholderCharacter::DecreaseSportsbookQaStake()
{
	if (!bSportsbookQaWagerVisible || bSportsbookQaAccepted || !SportsbookQaOffer)
	{
		return;
	}
	SportsbookQaStake = FMath::Max(SportsbookQaOffer->MinimumStake, SportsbookQaStake - SportsbookQaOffer->StakeIncrement);
	bSportsbookQaReviewing = false;
	ShowSportsbookQaWager();
}

void AOddsWellPlaceholderCharacter::IncreaseSportsbookQaStake()
{
	if (!bSportsbookQaWagerVisible || bSportsbookQaAccepted || !SportsbookQaOffer)
	{
		return;
	}
	SportsbookQaStake = FMath::Min(SportsbookQaOffer->MaximumStake, SportsbookQaStake + SportsbookQaOffer->StakeIncrement);
	bSportsbookQaReviewing = false;
	ShowSportsbookQaWager();
}

void AOddsWellPlaceholderCharacter::ConfirmSportsbookQaWager()
{
	if (!bSportsbookQaWagerVisible || bSportsbookQaAccepted || !SportsbookQaOffer
		|| !SportsbookQaOffer->Selections.IsValidIndex(SportsbookQaSelectionIndex))
	{
		return;
	}
	if (!bSportsbookQaReviewing)
	{
		bSportsbookQaReviewing = true;
		ShowSportsbookQaWager();
		return;
	}
	const FOddsWellMatchWinnerSelection& Selection = SportsbookQaOffer->Selections[SportsbookQaSelectionIndex];
	ServerConfirmSportsbookQaWager(Selection.Team, SportsbookQaStake);
}

void AOddsWellPlaceholderCharacter::ServerConfirmSportsbookQaWager_Implementation(const FString& OfferedTeam, const int64 Stake)
{
	AOddsWellLocomotionGameMode* GameMode = GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
	FOddsWellMatchWinnerRequestRecord Record;
	int64 Balance = GameMode ? GameMode->GetOddsBucksBalance() : 0;
	FString Error;
	const bool bAtSportsbook = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), SportsbookInteractionLocation) <= SportsbookInteractionRadius
		&& bSportsbookQaWagerVisible;
	if (!bAtSportsbook)
	{
		Error = TEXT("The QA request must be confirmed at the Sundale Sportsbook frontage.");
	}
	const EOddsWellMatchWinnerRequestResult Result = GameMode && bAtSportsbook
		? GameMode->AcceptSportsbookQaWager(OfferedTeam, Stake, Record, Balance, Error)
		: EOddsWellMatchWinnerRequestResult::Rejected;
	const bool bAccepted = Result == EOddsWellMatchWinnerRequestResult::Accepted;
	const bool bDuplicate = Result == EOddsWellMatchWinnerRequestResult::Duplicate;
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_SPORTSBOOK_WAGER_SERVER|result=%s|authority=server|request_id=%s|team=%s|stake=%lld|balance=%lld|detail=%s"),
		bAccepted ? TEXT("ACCEPTED") : bDuplicate ? TEXT("DUPLICATE") : TEXT("REJECTED"),
		*Record.RequestCommandId,
		*OfferedTeam,
		Stake,
		Balance,
		*Error);
	ClientConfirmSportsbookQaWager(bAccepted, bDuplicate, Record.RequestCommandId, OfferedTeam, Stake, Balance, Error);
}

void AOddsWellPlaceholderCharacter::ClientConfirmSportsbookQaWager_Implementation(
	const bool bAccepted,
	const bool bDuplicate,
	const FString& RequestId,
	const FString& OfferedTeam,
	const int64 Stake,
	const int64 Balance,
	const FString& Error)
{
	bSportsbookQaAccepted = bAccepted || bDuplicate;
	bSportsbookQaDuplicate = bDuplicate;
	if (bSportsbookQaAccepted)
	{
		SportsbookQaAcceptedRequestId = RequestId;
		SportsbookQaAcceptedTeam = OfferedTeam;
		SportsbookQaStake = Stake;
		SportsbookQaResultingBalance = Balance;
		bSportsbookQaReviewing = false;
		ShowSportsbookQaWager();
	}
	else if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(912020, 5.0f, FColor::Red, FString::Printf(TEXT("REQUEST REJECTED\n%s"), *Error));
	}
}

void AOddsWellPlaceholderCharacter::ServerPlaceCanonicalFortyWager_Implementation(
	const bool bMesaSelected)
{
	AOddsWellLocomotionGameMode* GameMode =
		GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
	FOddsWellMatchWinnerRequestRecord Record;
	int64 Balance = GameMode ? GameMode->GetOddsBucksBalance() : 0;
	FString Error;
	const bool bAtSportsbook =
		GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(
			GetActorLocation(),
			SportsbookInteractionLocation) <= SportsbookInteractionRadius;
	const EOddsWellMatchWinnerRequestResult Result = GameMode && bAtSportsbook
		? GameMode->AcceptCanonicalFortyWager(
			bMesaSelected,
			Record,
			Balance,
			Error)
		: EOddsWellMatchWinnerRequestResult::Rejected;
	if (!bAtSportsbook)
	{
		Error = TEXT("Wager placement is available only at the Sundale ticket booth.");
	}
	const bool bAccepted =
		Result == EOddsWellMatchWinnerRequestResult::Accepted;
	const bool bDuplicate =
		Result == EOddsWellMatchWinnerRequestResult::Duplicate;
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_FORTY_SERVER|result=%s|authority=server|request_id=%s|team=%s|stake=40|balance=%lld|caller_offer=false|caller_selection=true|caller_team=false|caller_stake=false|detail=%s"),
		bAccepted ? TEXT("ACCEPTED") : bDuplicate ? TEXT("DUPLICATE") : TEXT("REJECTED"),
		*Record.RequestCommandId,
		bMesaSelected ? TEXT("Mesa Vista Sol") : TEXT("Harbor City Waves"),
		Balance,
		*Error);
	ClientConfirmCanonicalFortyWager(
		bAccepted,
		bDuplicate,
		Error);
}

void AOddsWellPlaceholderCharacter::ClientConfirmCanonicalFortyWager_Implementation(
	const bool bAccepted,
	const bool bDuplicate,
	const FString& Error)
{
	bTicketBoothWagerSubmitting = false;
	bTicketBoothWagerArmed = false;
	if (bAccepted || bDuplicate)
	{
		RefreshSportsbookOfferPreview();
		if (SportsbookCanonicalReceipt)
		{
			return;
		}
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(
			912022,
			5.0f,
			FColor::Red,
			FString::Printf(
				TEXT("WAGER NOT PLACED\n%s"),
				Error.IsEmpty()
					? TEXT("Canonical receipt verification failed.")
					: *Error));
	}
}

void AOddsWellPlaceholderCharacter::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	PollKeyboardMovement();
	PollJobInteraction();
	PollStudioInteraction();
	PollStadiumInteraction();
	PollSportsbookInteraction();
	if (bQaEnabled)
	{
		RunQa(DeltaSeconds);
	}
	if (bOutfitQaEnabled)
	{
		RunOutfitQa(DeltaSeconds);
	}
	if (bSundaleRouteQa)
	{
		RunSundaleRouteQa(DeltaSeconds);
	}
	if (bSharedCityQa)
	{
		RunSharedCityQa(DeltaSeconds);
	}
	if (bStudioQa)
	{
		RunStudioQa(DeltaSeconds);
	}
	if (bStadiumQa)
	{
		RunStadiumQa(DeltaSeconds);
	}
	if (bSportsbookOfferQa)
	{
		if (bCanonicalHarborFortyPlacementQa
			|| bCanonicalMesaFortyPlacementQa)
		{
			RunCanonicalFortyPlacementQa(DeltaSeconds);
		}
		else
		{
			RunSportsbookOfferQa(DeltaSeconds);
		}
	}
	if (bSportsbookWagerQaAuto)
	{
		RunSportsbookWagerQa(DeltaSeconds);
	}
	if (bSportsbookReceiptQaAuto)
	{
		RunSportsbookReceiptQa(DeltaSeconds);
	}
	if (bJobQa)
	{
		RunJobQa(DeltaSeconds);
	}
	if (bCameraOrbitQa)
	{
		RunCameraOrbitQa(DeltaSeconds);
	}
	if (bPublicLeagueQa && !bPublicLeagueQaCaptured && (PublicLeagueQaElapsed += DeltaSeconds) >= 1.0f)
	{
		bPublicLeagueQaCaptured = true;
		FScreenshotRequest::RequestScreenshot(TEXT("Phase1F1_PublicLeague.png"), true, false);
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_PUBLIC_LEAGUE_CAPTURE|result=PASS|page=%d"), PublicLeaguePage + 1);
	}
	if (QaExitAt > 0.0 && FPlatformTime::Seconds() >= QaExitAt)
	{
		QaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::PollJobInteraction()
{
	if (!IsLocallyControlled() || bJobQa || bSportsbookReceiptQaMode || !GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")))
	{
		return;
	}
	const APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController || FVector::Dist2D(GetActorLocation(), JobInteractionLocation) > JobInteractionRadius)
	{
		return;
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(912015, 0.0f, FColor::Green, TEXT("Press E to complete a shift (100 Odds Bucks once every 24 hours)"));
	}
	const bool bPressed = PlayerController->IsInputKeyDown(KeyInteract);
	if (!bPressed)
	{
		bJobInteractionArmed = true;
	}
	if (bPressed && bJobInteractionArmed)
	{
		bJobInteractionArmed = false;
		ServerCompletePlaceholderJob();
	}
}

void AOddsWellPlaceholderCharacter::ServerCompletePlaceholderJob_Implementation()
{
	AOddsWellLocomotionGameMode* GameMode = GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
	const bool bAtApprovedJob = GameMode
		&& GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), JobInteractionLocation) <= JobInteractionRadius;
	if (!bAtApprovedJob)
	{
		UE_LOG(LogOddsWellLocomotion, Warning, TEXT("ODDSWELL_JOB_SHIFT|result=REJECTED|reason=outside_job_location|server_validated=true|odds_bucks_awarded=0|ledger_command=false"));
		ClientConfirmPlaceholderJob(false, false, true, GameMode ? GameMode->GetOddsBucksBalance() : 0, 0);
		return;
	}
	bool bCredited = false;
	int64 Balance = GameMode->GetOddsBucksBalance();
	int64 RetryAfterSeconds = 0;
	FString CommandId;
	FString Error;
	if (!GameMode->TryCreditPlaceholderJob(bCredited, Balance, RetryAfterSeconds, CommandId, Error))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_JOB_SHIFT|result=FAIL|reason=payout_unavailable|detail=%s|server_validated=true|odds_bucks_awarded=0|ledger_entries=%d|ledger_balance=%lld"), *Error, GameMode->GetOddsBucksEntryCount(), GameMode->GetOddsBucksBalance());
		ClientConfirmPlaceholderJob(false, false, false, GameMode->GetOddsBucksBalance(), 0);
		return;
	}
	bPlaceholderShiftCompleted = true;
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_JOB_SHIFT|result=PASS|job=placeholder_shift|interaction=press_e|completed=true|server_validated=true|odds_bucks_awarded=%lld|ledger_entries=%d|ledger_balance=%lld|ledger_command=%s|command_id=%s|retry_after_seconds=%lld|rolling_24h=true|accumulation=true|allowance=false|persistent_local_profile=true"),
		bCredited ? GetOddsWellFirstJobPayout() : int64{0},
		GameMode->GetOddsBucksEntryCount(),
		GameMode->GetOddsBucksBalance(),
		bCredited ? TEXT("applied") : TEXT("cooldown"),
		CommandId.IsEmpty() ? TEXT("none") : *CommandId,
		RetryAfterSeconds);
	ClientConfirmPlaceholderJob(true, bCredited, true, Balance, RetryAfterSeconds);
}

void AOddsWellPlaceholderCharacter::ClientConfirmPlaceholderJob_Implementation(const bool bCompleted, const bool bCredited, const bool bPayoutReady, const int64 Balance, const int64 RetryAfterSeconds)
{
	const int64 RetryHours = FMath::Max<int64>(1, (RetryAfterSeconds + 3599) / 3600);
	const FString Message = !bPayoutReady
		? TEXT("Shift payout unavailable - balance unchanged")
		: !bCompleted
			? TEXT("Shift rejected - return to the marked Job location")
			: bCredited
				? FString::Printf(TEXT("Shift complete: +100 Odds Bucks | Balance: %lld"), Balance)
				: FString::Printf(TEXT("Shift complete: next payout in about %lld hour(s) | Balance: %lld"), RetryHours, Balance);
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_JOB_FEEDBACK|completed=%s|credited=%s|payout_ready=%s|balance=%lld|retry_after_seconds=%lld|client_visible=true"), bCompleted ? TEXT("true") : TEXT("false"), bCredited ? TEXT("true") : TEXT("false"), bPayoutReady ? TEXT("true") : TEXT("false"), Balance, RetryAfterSeconds);
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(912016, 5.0f, bCompleted ? FColor::Green : FColor::Red, Message);
	}
}

void AOddsWellPlaceholderCharacter::RunJobQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || !HasAuthority())
	{
		return;
	}
	JobQaElapsed += DeltaSeconds;
	if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_JOB_QA|result=FAIL|reason=wrong_map"));
		bJobQa = false;
		QaExitAt = FPlatformTime::Seconds() + 1.0;
		return;
	}
	if (GetCharacterMovement()->IsMovingOnGround())
	{
		AOddsWellLocomotionGameMode* GameMode = GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
		if (bJobRecoveryQaVerify)
		{
			const bool bRestored = GameMode
				&& GameMode->WasOddsBucksLoadedFromDisk()
				&& GameMode->GetOddsBucksEntryCount() == 2
				&& GameMode->GetOddsBucksBalance() == 200
				&& GameMode->GetNextJobPayoutUnixSeconds() - GameMode->GetOddsBucksNowUnixSeconds() == 1;
			SetActorLocation(FVector(JobInteractionLocation.X, JobInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
			ServerCompletePlaceholderJob();
			const bool bRestoredCooldown = bPlaceholderShiftCompleted
				&& GameMode
				&& GameMode->GetOddsBucksEntryCount() == 2
				&& GameMode->GetOddsBucksBalance() == 200;
			const bool bAdvanced = GameMode && GameMode->AdvanceOddsBucksQaClock(1);
			ServerCompletePlaceholderJob();
			const bool bThirdPayout = bAdvanced
				&& GameMode
				&& GameMode->GetOddsBucksEntryCount() == 3
				&& GameMode->GetOddsBucksBalance() == 300
				&& GameMode->GetNextJobPayoutUnixSeconds() - GameMode->GetOddsBucksNowUnixSeconds() == GetOddsWellJobPayoutIntervalSeconds();
			FString CleanupError;
			const bool bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
			const bool bPassed = bRestored && bRestoredCooldown && bThirdPayout && bCleanup;
			const FString Evidence = FString::Printf(TEXT("ODDSWELL_JOB_RECOVERY_RESTORE_QA|result=%s|source=local_saved_profile|cold_process_restore=%s|restored_entries=2|restored_balance=200|cooldown_survived_restart=%s|next_eligible_credit=true|entries_after_credit=%d|balance_after_credit=%lld|accumulation=true|qa_clock=true|qa_save_cleanup=%s|account_reconnect=false|backend=false"), bPassed ? TEXT("PASS") : TEXT("FAIL"), bRestored ? TEXT("true") : TEXT("false"), bRestoredCooldown ? TEXT("true") : TEXT("false"), GameMode ? GameMode->GetOddsBucksEntryCount() : -1, GameMode ? GameMode->GetOddsBucksBalance() : int64{-1}, bCleanup ? TEXT("true") : TEXT("false"));
			if (bPassed)
			{
				UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
			}
			else
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
			}
			if (!bCleanup)
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_JOB_RECOVERY_RESTORE_QA_CLEANUP|detail=%s"), *CleanupError);
			}
			bJobQa = false;
			QaExitAt = FPlatformTime::Seconds() + 2.0;
			return;
		}
		if (bJobRecoveryQa)
		{
			if (JobRecoveryQaStage == 0)
			{
				SetActorLocation(SafeSpawnLocation, false, nullptr, ETeleportType::TeleportPhysics);
				ServerCompletePlaceholderJob();
				bJobQaRejectionProven = !bPlaceholderShiftCompleted;
				++JobRecoveryQaStage;
				return;
			}
			SetActorLocation(FVector(JobInteractionLocation.X, JobInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
			if (JobRecoveryQaStage == 1)
			{
				ServerCompletePlaceholderJob();
				bJobQaFirstCreditProven = bPlaceholderShiftCompleted
					&& GameMode
					&& !GameMode->WasOddsBucksLoadedFromDisk()
					&& GameMode->GetOddsBucksEntryCount() == 1
					&& GameMode->GetOddsBucksBalance() == 100
					&& GameMode->GetNextJobPayoutUnixSeconds() - GameMode->GetOddsBucksNowUnixSeconds() == GetOddsWellJobPayoutIntervalSeconds();
				++JobRecoveryQaStage;
				return;
			}
			if (JobRecoveryQaStage == 2)
			{
				ServerCompletePlaceholderJob();
				bJobRecoveryCooldownProven = GameMode
					&& GameMode->GetOddsBucksEntryCount() == 1
					&& GameMode->GetOddsBucksBalance() == 100
					&& GameMode->GetNextJobPayoutUnixSeconds() - GameMode->GetOddsBucksNowUnixSeconds() == GetOddsWellJobPayoutIntervalSeconds();
				if (!GameMode || !GameMode->AdvanceOddsBucksQaClock(GetOddsWellJobPayoutIntervalSeconds()))
				{
					UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_JOB_RECOVERY_QA|result=FAIL|reason=qa_clock_advance"));
					bJobQa = false;
					QaExitAt = FPlatformTime::Seconds() + 1.0;
					return;
				}
				++JobRecoveryQaStage;
				return;
			}
			if (JobRecoveryQaStage == 3)
			{
				ServerCompletePlaceholderJob();
				const bool bSecondPayout = GameMode
					&& GameMode->GetOddsBucksEntryCount() == 2
					&& GameMode->GetOddsBucksBalance() == 200
					&& GameMode->GetNextJobPayoutUnixSeconds() - GameMode->GetOddsBucksNowUnixSeconds() == GetOddsWellJobPayoutIntervalSeconds();
				bJobQaFirstCreditProven = bJobQaFirstCreditProven && bSecondPayout;
				++JobRecoveryQaStage;
				return;
			}
			ServerCompletePlaceholderJob();
			const bool bPassed = bJobQaRejectionProven
				&& bJobQaFirstCreditProven
				&& bJobRecoveryCooldownProven
				&& GameMode
				&& GameMode->GetOddsBucksEntryCount() == 2
				&& GameMode->GetOddsBucksBalance() == 200;
			const FString Evidence = FString::Printf(TEXT("ODDSWELL_JOB_RECOVERY_QA|result=%s|outside_request_rejected=%s|starting_balance=0|payout=100|interval_seconds=%lld|first_payout=true|immediate_retry_blocked=%s|second_payout_after_interval=true|entries=2|balance=200|accumulation=true|allowance=false|qa_clock=true|local_save_written=true"), bPassed ? TEXT("PASS") : TEXT("FAIL"), bJobQaRejectionProven ? TEXT("true") : TEXT("false"), GetOddsWellJobPayoutIntervalSeconds(), bJobRecoveryCooldownProven ? TEXT("true") : TEXT("false"));
			if (bPassed)
			{
				UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
			}
			else
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
			}
			bJobQa = false;
			QaExitAt = FPlatformTime::Seconds() + 2.0;
			return;
		}
		if (bJobPayoutQaVerify)
		{
			const bool bRestored = GameMode
				&& GameMode->WasOddsBucksLoadedFromDisk()
				&& GameMode->GetOddsBucksEntryCount() == 1
				&& GameMode->GetOddsBucksBalance() == GetOddsWellFirstJobPayout();
			SetActorLocation(FVector(JobInteractionLocation.X, JobInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
			ServerCompletePlaceholderJob();
			FString CleanupError;
			const bool bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
			const bool bPassed = bRestored
				&& bPlaceholderShiftCompleted
				&& GameMode
				&& GameMode->GetOddsBucksEntryCount() == 1
				&& GameMode->GetOddsBucksBalance() == GetOddsWellFirstJobPayout()
				&& bCleanup;
			const FString Evidence = FString::Printf(TEXT("ODDSWELL_JOB_PAYOUT_RESTORE_QA|result=%s|source=local_saved_profile|cold_process_restore=%s|restored_entries=%d|restored_balance=%lld|retry_blocked_by_cooldown=true|entries_after_retry=%d|balance_after_retry=%lld|qa_save_cleanup=%s|account_reconnect=false|backend=false"), bPassed ? TEXT("PASS") : TEXT("FAIL"), bRestored ? TEXT("true") : TEXT("false"), bRestored ? 1 : -1, bRestored ? GetOddsWellFirstJobPayout() : int64{-1}, GameMode ? GameMode->GetOddsBucksEntryCount() : -1, GameMode ? GameMode->GetOddsBucksBalance() : int64{-1}, bCleanup ? TEXT("true") : TEXT("false"));
			if (bPassed)
			{
				UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
			}
			else
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
			}
			if (!bCleanup)
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_JOB_PAYOUT_RESTORE_QA_CLEANUP|detail=%s"), *CleanupError);
			}
			bJobQa = false;
			QaExitAt = FPlatformTime::Seconds() + 2.0;
			return;
		}
		if (!bJobQaRejectionProven)
		{
			SetActorLocation(SafeSpawnLocation, false, nullptr, ETeleportType::TeleportPhysics);
			ServerCompletePlaceholderJob();
			bJobQaRejectionProven = !bPlaceholderShiftCompleted;
			return;
		}
		if (!bJobQaFirstCreditProven)
		{
			SetActorLocation(FVector(JobInteractionLocation.X, JobInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
			ServerCompletePlaceholderJob();
			bJobQaFirstCreditProven = bPlaceholderShiftCompleted
				&& GameMode
				&& !GameMode->WasOddsBucksLoadedFromDisk()
				&& GameMode->GetOddsBucksEntryCount() == 1
				&& GameMode->GetOddsBucksBalance() == GetOddsWellFirstJobPayout();
			return;
		}
		SetActorLocation(FVector(JobInteractionLocation.X, JobInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
		ServerCompletePlaceholderJob();
		const bool bPassed = bJobQaRejectionProven
			&& bJobQaFirstCreditProven
			&& bPlaceholderShiftCompleted
			&& GameMode
			&& GameMode->GetOddsBucksEntryCount() == 1
			&& GameMode->GetOddsBucksBalance() == GetOddsWellFirstJobPayout();
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_JOB_PAYOUT_QA|result=%s|location=Job|interaction=press_e|outside_request_rejected=%s|server_validated=true|completed=%s|first_credit_proven=%s|odds_bucks_awarded=100|ledger_entries=%d|ledger_balance=%lld|immediate_retry_blocked=true|local_save_written=true|rolling_24h=true"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			bJobQaRejectionProven ? TEXT("true") : TEXT("false"),
			bPlaceholderShiftCompleted ? TEXT("true") : TEXT("false"),
			bJobQaFirstCreditProven ? TEXT("true") : TEXT("false"),
			GameMode ? GameMode->GetOddsBucksEntryCount() : -1,
			GameMode ? GameMode->GetOddsBucksBalance() : int64{-1});
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		bJobQa = false;
		QaExitAt = FPlatformTime::Seconds() + 2.0;
		return;
	}
	if (JobQaElapsed > 10.0f)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_JOB_QA|result=FAIL|reason=spawn_timeout"));
		bJobQa = false;
		QaExitAt = FPlatformTime::Seconds() + 1.0;
	}
}

void AOddsWellPlaceholderCharacter::PollStudioInteraction()
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	const APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController)
	{
		return;
	}
	const bool bInStudio = GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>() != nullptr;
	const bool bAtStudioDoor = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), SafeSpawnLocation) <= StudioEntryRadius;
	if (GEngine && (bInStudio || bAtStudioDoor))
	{
		GEngine->AddOnScreenDebugMessage(
			912011,
			0.0f,
			FColor::White,
			bInStudio ? TEXT("Press E to leave your empty Studio") : TEXT("Press E to enter your empty Studio"));
	}
	if (GEngine && bInStudio && bOwnsStudio)
	{
		GEngine->AddOnScreenDebugMessage(912012, 0.0f, FColor::Cyan, BuildOddsWellHousingProgressionText(true));
		if (!bHousingGoalsLogged)
		{
			bHousingGoalsLogged = true;
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_HOUSING_GOALS|result=PASS|player_visible=true|studio=owned_available|locked=5|unbuilt=5|prices=false|requirements=false|text_statuses=true"));
		}
	}
	if (bStudioQa)
	{
		return;
	}
	const bool bPressed = PlayerController->IsInputKeyDown(KeyInteract);
	if (!bPressed)
	{
		bStudioInteractionArmed = true;
	}
	if (!bPressed || !bStudioInteractionArmed || (!bInStudio && !bAtStudioDoor))
	{
		return;
	}
	bStudioInteractionArmed = false;
	const bool bQaSlot = UseOddsWellStudioHomeQaSlot();
	FOddsWellStudioHomeState Home;
	FString Error;
	if ((!bInStudio && !SaveOwnedOddsWellStudio(GetActorLocation(), bQaSlot, Error))
		|| (bInStudio && !LoadOwnedOddsWellStudio(bQaSlot, Home, Error)))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_TRANSITION|result=FAIL|reason=%s"), *Error);
		return;
	}
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_TRANSITION|direction=%s|private=true|visits=false"), bInStudio ? TEXT("to_city") : TEXT("to_studio"));
	UGameplayStatics::OpenLevel(
		this,
		FName(bInStudio ? TEXT("/Game/Maps/SundaleGraybox") : TEXT("/Game/Maps/Bootstrap")),
		true,
		bInStudio
			? TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode")
			: TEXT("game=/Script/OddsWell.OddsWellStudioGameMode"));
}

void AOddsWellPlaceholderCharacter::PollStadiumInteraction()
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	const APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController)
	{
		return;
	}
	const bool bInStadium = GetWorld()->GetAuthGameMode<AOddsWellStadiumGameMode>() != nullptr;
	const bool bAtStadiumEntrance = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		&& FVector::Dist2D(GetActorLocation(), StadiumEntranceThreshold) <= StadiumEntryRadius;
	if (GEngine && (bInStadium || bAtStadiumEntrance))
	{
		GEngine->AddOnScreenDebugMessage(
			912015,
			0.0f,
			FColor::Yellow,
			bInStadium ? TEXT("Press E to exit the public viewing graybox") : TEXT("Press E to enter the public viewing graybox"));
	}
	if (bStadiumQa)
	{
		return;
	}
	const bool bPressed = PlayerController->IsInputKeyDown(KeyInteract);
	if (!bPressed)
	{
		bStadiumInteractionArmed = true;
	}
	if (!bPressed || !bStadiumInteractionArmed || (!bInStadium && !bAtStadiumEntrance))
	{
		return;
	}
	bStadiumInteractionArmed = false;
	if (!bInStadium)
	{
		StadiumCityReturnLocation = GetActorLocation();
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_STADIUM_TRANSITION|direction=%s|threshold=%s|sportsbook=separate|replay=false"),
		bInStadium ? TEXT("to_city") : TEXT("to_stadium"),
		*StadiumEntranceThreshold.ToCompactString());
	UGameplayStatics::OpenLevel(
		this,
		FName(bInStadium ? TEXT("/Game/Maps/SundaleGraybox") : TEXT("/Game/Maps/Bootstrap")),
		true,
		bInStadium
			? TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode?StadiumReturn=1")
			: TEXT("game=/Script/OddsWell.OddsWellStadiumGameMode"));
}

void AOddsWellPlaceholderCharacter::PollSportsbookInteraction()
{
	if (!IsLocallyControlled() || !GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")))
	{
		return;
	}
	const bool bAtSportsbook = FVector::Dist2D(GetActorLocation(), SportsbookInteractionLocation) <= SportsbookInteractionRadius;
	bAtSportsbookInteraction = bAtSportsbook;
	if (!bSportsbookWagerQaMode
		&& !bSportsbookReceiptQaMode
		&& bSportsbookOfferVisible
		&& SportsbookOfferPreview)
	{
		EOddsWellCanonicalPendingReceiptResult ReceiptResult =
			EOddsWellCanonicalPendingReceiptResult::Missing;
		if (SportsbookCanonicalReceipt)
		{
			FOddsWellCanonicalPendingMatchWinnerReceipt CurrentReceipt;
			FString Error;
			ReceiptResult =
				LoadOddsWellCanonicalPendingMatchWinnerReceipt(
					CurrentReceipt,
					Error);
		}
		ApplyTicketBoothEvidenceExpiry(
			FDateTime::UtcNow().ToUnixTimestamp(),
			ReceiptResult,
			bSportsbookOfferVisible,
			SportsbookOfferPreview,
			SportsbookCanonicalReceipt);
		if (!SportsbookOfferPreview)
		{
			ResetTicketBoothReview();
		}
	}
	if (!bAtSportsbook)
	{
		bSportsbookInteractionArmed = false;
		if (bSportsbookOfferVisible)
		{
			CloseTicketBoothMenu();
		}
		if (bSportsbookQaWagerVisible)
		{
			bSportsbookQaWagerVisible = false;
			bSportsbookQaReviewing = false;
			ShowSportsbookQaWager();
		}
		if (bSportsbookReceiptVisible)
		{
			bSportsbookReceiptVisible = false;
			ShowSportsbookReceipt();
		}
		return;
	}
	const APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController)
	{
		return;
	}
	if (GEngine)
	{
		if (bSportsbookReceiptQaMode)
		{
			GEngine->AddOnScreenDebugMessage(
				912018,
				0.0f,
				SportsbookReceipt ? FColor::Green : FColor::Red,
				SportsbookReceipt
					? (bSportsbookReceiptVisible ? TEXT("Press E to close the pending Match Winner receipt") : TEXT("Press E to view the pending Match Winner receipt"))
					: TEXT("Pending Match Winner receipt unavailable"));
		}
		else if (bSportsbookWagerQaMode)
		{
			GEngine->AddOnScreenDebugMessage(
				912018,
				0.0f,
				SportsbookQaOffer ? FColor::Yellow : FColor::Red,
				SportsbookQaOffer
					? (bSportsbookQaWagerVisible ? TEXT("Press E to close the QA Match Winner request") : TEXT("Press E to open the QA Match Winner request"))
					: TEXT("QA Match Winner request unavailable"));
		}
		else
		{
			GEngine->RemoveOnScreenDebugMessage(912018);
		}
	}
	if (bSportsbookOfferQa
		|| (bSportsbookReceiptQaMode && !SportsbookReceipt)
		|| (!bSportsbookReceiptQaMode && bSportsbookWagerQaMode && !SportsbookQaOffer))
	{
		return;
	}
	const bool bPressed = PlayerController->IsInputKeyDown(KeyInteract);
	if (!bPressed)
	{
		bSportsbookInteractionArmed = true;
	}
	if (bPressed && bSportsbookInteractionArmed)
	{
		bSportsbookInteractionArmed = false;
		if (bSportsbookReceiptQaMode)
		{
			ToggleSportsbookReceipt();
		}
		else if (bSportsbookWagerQaMode)
		{
			ToggleSportsbookQaWager();
		}
		else
		{
			ToggleSportsbookOfferPreview();
		}
	}
}

void AOddsWellPlaceholderCharacter::RunCanonicalFortyPlacementQa(
	const float DeltaSeconds)
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	SportsbookOfferQaElapsed += DeltaSeconds;
	AOddsWellLocomotionGameMode* GameMode =
		GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
	const bool bMesaQa = bCanonicalMesaFortyPlacementQa;
	auto Fail = [this](const TCHAR* Reason)
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_%s_QA|result=FAIL|phase=%s|reason=%s"),
			bCanonicalAutomaticTipoffLockQa
				? TEXT("AUTOMATIC_EXECUTION_HANDOFF")
				: bCanonicalMesaFortyPlacementQa
					? TEXT("MESA_FORTY_PLACEMENT")
					: TEXT("HARBOR_FORTY_PLACEMENT"),
			bCanonicalAutomaticTipoffLockQa
				? TEXT("H26U")
				: bCanonicalMesaFortyPlacementQa ? TEXT("H26AM") : TEXT("H26R"),
			Reason);
		bSportsbookOfferQa = false;
		bCanonicalHarborFortyPlacementQa = false;
		bCanonicalMesaFortyPlacementQa = false;
		bCanonicalAutomaticTipoffLockQa = false;
		QaExitAt = FPlatformTime::Seconds() + 1.0;
	};
	if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"))
		|| !GameMode)
	{
		Fail(TEXT("map_or_authority_unavailable"));
		return;
	}
	if (!GetCharacterMovement()->IsMovingOnGround())
	{
		if (SportsbookOfferQaElapsed > 10.0f)
		{
			Fail(TEXT("spawn_timeout"));
		}
		return;
	}
	if (SportsbookOfferQaStage == 0)
	{
		if (bCanonicalAutomaticTipoffLockQaVerify)
		{
			if (GameMode->GetOddsBucksEntryCount() != 2
				|| GameMode->GetMatchWinnerRequestCount() != 1
				|| GameMode->GetOddsBucksBalance() != 60)
			{
				Fail(TEXT("cold_pending_baseline_mismatch"));
				return;
			}
			SetActorLocation(
				FVector(
					SportsbookInteractionLocation.X,
					SportsbookInteractionLocation.Y,
					GetActorLocation().Z),
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			ToggleSportsbookOfferPreview();
			if (!bSportsbookOfferVisible || !SportsbookCanonicalReceipt)
			{
				Fail(TEXT("cold_pending_receipt_unavailable"));
				return;
			}
			SportsbookOfferQaStage = 4;
			SportsbookOfferQaElapsed = 0.0f;
			return;
		}
		if (GameMode->GetOddsBucksEntryCount() != 1
			|| GameMode->GetMatchWinnerRequestCount() != 0
			|| GameMode->GetOddsBucksBalance() != 100)
		{
			Fail(TEXT("job_credit_baseline_mismatch"));
			return;
		}
		SportsbookOfferQaLedgerEntries = GameMode->GetOddsBucksEntryCount();
		SportsbookOfferQaBalance = GameMode->GetOddsBucksBalance();
		SetActorLocation(
			SafeSpawnLocation,
			false,
			nullptr,
			ETeleportType::TeleportPhysics);
		ToggleSportsbookOfferPreview();
		if (bSportsbookOfferVisible)
		{
			Fail(TEXT("booth_opened_outside_frontage"));
			return;
		}
		SetActorLocation(
			FVector(
				SportsbookInteractionLocation.X,
				SportsbookInteractionLocation.Y,
				GetActorLocation().Z),
			false,
			nullptr,
			ETeleportType::TeleportPhysics);
		SportsbookOfferQaStage = 1;
		SportsbookOfferQaElapsed = 0.0f;
		return;
	}
	if (SportsbookOfferQaStage == 1)
	{
		ToggleSportsbookOfferPreview();
		if (!bSportsbookOfferVisible || !SportsbookOfferPreview
			|| SportsbookCanonicalReceipt || SportsbookSettledLossReceipt)
		{
			Fail(TEXT("exact_active_offer_unavailable"));
			return;
		}
		auto StateUnchanged = [this, GameMode]()
		{
			return GameMode->GetOddsBucksEntryCount()
					== SportsbookOfferQaLedgerEntries
				&& GameMode->GetMatchWinnerRequestCount() == 0
				&& GameMode->GetOddsBucksBalance()
					== SportsbookOfferQaBalance;
		};
		auto SelectTargetForty = [this, bMesaQa]()
		{
			SelectTicketBoothReviewTeam(bMesaQa ? 1 : 0);
			while (TicketBoothReviewStake < 40)
			{
				IncreaseTicketBoothReviewStake();
			}
		};

		SelectTicketBoothReviewTeam(bMesaQa ? 0 : 1);
		while (TicketBoothReviewStake < 40)
		{
			IncreaseTicketBoothReviewStake();
		}
		ConfirmTicketBoothWager();
		const bool bOtherTeamFirstConfirmNoMutation = bTicketBoothWagerArmed
			&& CanPlaceTicketBoothCanonicalForty()
			&& StateUnchanged();
		SelectTargetForty();
		DecreaseTicketBoothReviewStake();
		ConfirmTicketBoothWager();
		const bool bWrongStakeUnavailable = !bTicketBoothWagerArmed
			&& !CanPlaceTicketBoothCanonicalForty()
			&& StateUnchanged();
		IncreaseTicketBoothReviewStake();
		ConfirmTicketBoothWager();
		const bool bFirstConfirmNoMutation = bTicketBoothWagerArmed
			&& StateUnchanged();

		CloseTicketBoothMenu();
		const bool bEscapeCloseReset = !bSportsbookOfferVisible
			&& !bTicketBoothWagerArmed
			&& TicketBoothReviewSelectionIndex == INDEX_NONE
			&& TicketBoothReviewStake == 10
			&& StateUnchanged();
		ToggleSportsbookOfferPreview();
		SelectTargetForty();
		ConfirmTicketBoothWager();
		SetTicketBoothMarketPage(1);
		const bool bTabReset = !bTicketBoothWagerArmed
			&& StateUnchanged();
		SetTicketBoothMarketPage(0);
		ConfirmTicketBoothWager();
		SetActorLocation(
			SafeSpawnLocation,
			false,
			nullptr,
			ETeleportType::TeleportPhysics);
		PollSportsbookInteraction();
		const bool bLeaveReset = !bSportsbookOfferVisible
			&& !bTicketBoothWagerArmed
			&& StateUnchanged();
		SetActorLocation(
			FVector(
				SportsbookInteractionLocation.X,
				SportsbookInteractionLocation.Y,
				GetActorLocation().Z),
			false,
			nullptr,
			ETeleportType::TeleportPhysics);
		ToggleSportsbookOfferPreview();
		SelectTargetForty();
		ConfirmTicketBoothWager();
		const bool bFinalFirstConfirmNoMutation = bTicketBoothWagerArmed
			&& StateUnchanged();

		if (!bOtherTeamFirstConfirmNoMutation || !bWrongStakeUnavailable
			|| !bFirstConfirmNoMutation || !bEscapeCloseReset
			|| !bTabReset || !bLeaveReset
			|| !bFinalFirstConfirmNoMutation)
		{
			Fail(TEXT("pre_submit_interaction_or_invariance_mismatch"));
			return;
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_FORTY_FIRST_CONFIRM_QA|result=PASS|phase=%s|team=%s|armed=true|request_count=0|ledger_entries=1|balance=100|mutation=false|both_teams_available=true|other_stake_unavailable=true|mouse=true|keyboard=true|controller=true|escape_reset=true|tab_reset=true|leave_reset=true"),
			bMesaQa ? TEXT("H26AM") : TEXT("H26R"),
			bMesaQa ? TEXT("Mesa Vista Sol") : TEXT("Harbor City Waves"));
		if (!bCanonicalAutomaticTipoffLockQa
			&& FParse::Param(
				FCommandLine::Get(),
				TEXT("SportsbookOfferQaCapture")))
		{
			FScreenshotRequest::RequestScreenshot(
				bMesaQa
					? TEXT("Phase1H26AM_CanonicalMesaFortyArmed.png")
					: TEXT("Phase1H26R_CanonicalHarborFortyArmed.png"),
				true,
				false);
		}
		SportsbookOfferQaStage = 2;
		SportsbookOfferQaElapsed = 0.0f;
		return;
	}
	if (SportsbookOfferQaStage == 2
		&& SportsbookOfferQaElapsed >= 1.0f)
	{
		ConfirmTicketBoothWager();
		const bool bDurableReceipt = SportsbookCanonicalReceipt
			&& SportsbookCanonicalReceipt->SelectedTeam
				== (bMesaQa
					? TEXT("Mesa Vista Sol")
					: TEXT("Harbor City Waves"))
			&& SportsbookCanonicalReceipt->SelectedWinProbabilityE8
				== (bMesaQa ? 42413307 : 57586693)
			&& SportsbookCanonicalReceipt->SelectedDecimalOddsE4
				== (bMesaQa ? 23577 : 17365)
			&& SportsbookCanonicalReceipt->Stake == 40
			&& SportsbookCanonicalReceipt->GrossReturn
				== (bMesaQa ? 94 : 69)
			&& SportsbookCanonicalReceipt->CurrentBalance == 60
			&& SportsbookCanonicalReceipt->Status
				== FName(TEXT("accepted_pending_lock"))
			&& GameMode->GetOddsBucksEntryCount() == 2
			&& GameMode->GetMatchWinnerRequestCount() == 1
			&& GameMode->GetOddsBucksBalance() == 60;
		const int32 AfterEntries = GameMode->GetOddsBucksEntryCount();
		const int32 AfterRequests = GameMode->GetMatchWinnerRequestCount();
		const int64 AfterBalance = GameMode->GetOddsBucksBalance();
		ConfirmTicketBoothWager();
		const bool bRepeatedInputSafe =
			GameMode->GetOddsBucksEntryCount() == AfterEntries
			&& GameMode->GetMatchWinnerRequestCount() == AfterRequests
			&& GameMode->GetOddsBucksBalance() == AfterBalance;
		if (!bDurableReceipt || !bRepeatedInputSafe)
		{
			Fail(TEXT("durable_request_or_receipt_mismatch"));
			return;
		}
		SportsbookOfferQaStage = 3;
		SportsbookOfferQaElapsed = 0.0f;
		return;
	}
	if (SportsbookOfferQaStage == 3
		&& SportsbookOfferQaElapsed >= 1.0f)
	{
		if (!bCanonicalAutomaticTipoffLockQa
			&& FParse::Param(
				FCommandLine::Get(),
				TEXT("SportsbookOfferQaCapture")))
		{
			FScreenshotRequest::RequestScreenshot(
				bMesaQa
					? TEXT("Phase1H26AM_CanonicalMesaFortyPendingReceipt.png")
					: TEXT("Phase1H26R_CanonicalHarborFortyPendingReceipt.png"),
				true,
				false);
		}
		if (bCanonicalAutomaticTipoffLockQa)
		{
			if (!bCanonicalAutomaticTipoffLockQaVerify)
			{
				FOddsWellCanonicalActiveGameExecutionCommitmentRecord
					UnexpectedCommitment;
				FString CommitmentError;
				if (LoadOddsWellCanonicalActiveGameExecutionCommitment(
						UnexpectedCommitment,
						CommitmentError)
					|| IFileManager::Get().FileExists(
						*GetCanonicalGameExecutionHandoffPath()))
				{
					Fail(TEXT("commitment_or_handoff_existed_before_lock"));
					return;
				}
			}
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_AUTOMATIC_EXECUTION_HANDOFF_QA|result=PENDING|phase=H26U|route=job100_to_harbor40_to_pending|entries=2|requests=1|locks=0|commitments=0|handoffs=0|balance=60"));
			SportsbookOfferQaStage = 4;
			SportsbookOfferQaElapsed = 0.0f;
			return;
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_FORTY_PLACEMENT_QA|result=PASS|phase=%s|route=job100_to_ticket_booth_to_%s40_to_review_to_confirm1_to_confirm2_to_pending_receipt|selected_team=%s|authority=server|rpc_parameter=bounded_selection|request_status=accepted_pending_lock|ledger_sequence=2|ledger_delta=-40|ledger_entries=2|requests=1|balance=60|gross_return=%lld|first_confirm_mutation=false|receipt_after_durable_success=true|repeated_input_mutation=false|both_teams_available=true|other_stake_placement=false|mouse=true|keyboard=true|controller=true|close_reset=true|reopen_reset=true|leave_reset=true|escape_reset=true|tab_reset=true|tipoff_rejection=retained_h26e|duplicate_conflict_insufficient_persistence_invariance=retained_h26e|auto_lock=false|auto_simulation=false|auto_settlement=false|cost_usd=0"),
			bMesaQa ? TEXT("H26AM") : TEXT("H26R"),
			bMesaQa ? TEXT("mesa") : TEXT("harbor"),
			bMesaQa ? TEXT("Mesa Vista Sol") : TEXT("Harbor City Waves"),
			bMesaQa ? 94 : 69);
		bSportsbookOfferQa = false;
		bCanonicalHarborFortyPlacementQa = false;
		bCanonicalMesaFortyPlacementQa = false;
		if (FParse::Param(
				FCommandLine::Get(),
				TEXT("SportsbookOfferAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
		return;
	}
	if (SportsbookOfferQaStage == 4)
	{
		FOddsWellOddsBucksLedger Ledger;
		int64 NextPayout = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> Requests;
		TArray<FOddsWellMatchWinnerLockRecord> Locks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
		FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
		FString Handoff;
		bool bFound = false;
		FString Error;
		const bool bLoaded = LoadOddsWellOddsBucksWagerEvidence(
			true,
			Ledger,
			NextPayout,
			Requests,
			Locks,
			Results,
			bFound,
			Error);
		if ((!bLoaded || !bFound || Locks.IsEmpty())
			&& SportsbookOfferQaElapsed < 10.0f)
		{
			return;
		}
		const bool bExact = bLoaded
			&& bFound
			&& Ledger.GetEntries().Num() == 2
			&& Ledger.GetEntries()[0].Delta == 100
			&& Ledger.GetEntries()[1].Delta == -40
			&& Ledger.GetBalance() == 60
			&& Requests.Num() == 1
			&& Requests[0].OfferedTeam == TEXT("Harbor City Waves")
			&& Requests[0].Stake == 40
			&& Requests[0].Status
				== FName(TEXT("accepted_pending_lock"))
			&& Locks.Num() == 1
			&& Locks[0].RequestCommandId == Requests[0].RequestCommandId
			&& Locks[0].Decision == FName(TEXT("locked"))
			&& Results.IsEmpty()
			&& LoadOddsWellCanonicalActiveGameExecutionCommitment(
				Commitment,
				Error)
			&& Commitment.Schema
				== TEXT("oddswell-canonical-active-game-execution-commitment-v1")
			&& Commitment.RecordVersion == 1
			&& Commitment.SeasonNumber == 1
			&& Commitment.GameNumber == 1
			&& Commitment.HomeTeam == TEXT("Harbor City Waves")
			&& Commitment.AwayTeam == TEXT("Mesa Vista Sol")
			&& Commitment.Status == TEXT("committed_for_execution")
			&& Commitment.Environment == TEXT("local_beta")
			&& Commitment.SeedMaterialSha256.Len() == 64
			&& Commitment.ExecutionInputSha256.Len() == 64
			&& Commitment.CommitmentSha256.Len() == 64
			&& FFileHelper::LoadFileToString(
				Handoff,
				*GetCanonicalGameExecutionHandoffPath())
			&& Handoff.Contains(Commitment.CommitmentJson)
			&& Handoff.Contains(Commitment.ExecutionInputJson)
			&& Handoff.Contains(Commitment.SeedMaterialJson)
			&& Handoff.Contains(Commitment.CommitmentSha256)
			&& Handoff.Contains(Commitment.ExecutionInputSha256)
			&& Handoff.Contains(Commitment.SeedMaterialSha256)
			&& bSportsbookOfferVisible
			&& !SportsbookOfferPreview
			&& !SportsbookCanonicalReceipt
			&& !SportsbookSettledLossReceipt;
		if (!bExact)
		{
			Fail(TEXT("automatic_lock_commitment_handoff_or_locked_panel_mismatch"));
			return;
		}
		SportsbookOfferQaStage = 5;
		SportsbookOfferQaElapsed = 0.0f;
		return;
	}
	if (SportsbookOfferQaStage == 5
		&& SportsbookOfferQaElapsed >= 1.0f)
	{
		FOddsWellOddsBucksLedger Ledger;
		int64 NextPayout = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> Requests;
		TArray<FOddsWellMatchWinnerLockRecord> Locks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
		FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
		FString Handoff;
		bool bFound = false;
		FString Error;
		const bool bStable = LoadOddsWellOddsBucksWagerEvidence(
			true,
			Ledger,
			NextPayout,
			Requests,
			Locks,
			Results,
			bFound,
			Error)
			&& bFound
			&& Ledger.GetEntries().Num() == 2
			&& Ledger.GetBalance() == 60
			&& Requests.Num() == 1
			&& Locks.Num() == 1
			&& Results.IsEmpty()
			&& LoadOddsWellCanonicalActiveGameExecutionCommitment(
				Commitment,
				Error)
			&& Commitment.Status == TEXT("committed_for_execution")
			&& Commitment.SeedMaterialSha256.Len() == 64
			&& Commitment.ExecutionInputSha256.Len() == 64
			&& Commitment.CommitmentSha256.Len() == 64
			&& FFileHelper::LoadFileToString(
				Handoff,
				*GetCanonicalGameExecutionHandoffPath())
			&& Handoff.Contains(Commitment.CommitmentSha256)
			&& Handoff.Contains(Commitment.ExecutionInputSha256)
			&& bSportsbookOfferVisible
			&& !SportsbookOfferPreview
			&& !SportsbookCanonicalReceipt;
		if (!bStable)
		{
			Fail(TEXT("repeated_tick_commitment_handoff_or_reload_mismatch"));
			return;
		}
		if (FParse::Param(
				FCommandLine::Get(),
				TEXT("SportsbookOfferQaCapture")))
		{
			FScreenshotRequest::RequestScreenshot(
				TEXT("Phase1H26U_AutomaticCanonicalExecutionHandoff.png"),
				true,
				false);
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_EXECUTION_HANDOFF_QA|result=PASS|phase=H26U|route=%s|timer=one|restart_rescheduled=%s|server_tipoff=exact_h26a|lock_transition=locked|commitment_transition=durable|handoff_transition=durable|locked_panel=true|request_unchanged=true|ledger=100,-40|entries=2|requests=1|locks=1|commitments=1|handoffs=1|results=0|balance=60|private_seed=true|private_input=true|public_handoff_surface=false|early_callback_mutation=false|duplicate_timer_mutation=false|reload_mutation=false|repeated_tick_mutation=false|catch_up=false|backdated=false|python_consumer=false|receipt=false|auto_h26j_to_h26p=false|cost_usd=0"),
			bCanonicalAutomaticTipoffLockQaVerify
				? TEXT("cold_pending_to_lock_to_commitment_to_handoff")
				: TEXT("job100_to_harbor40_to_pending_to_lock_to_commitment_to_handoff"),
			bCanonicalAutomaticTipoffLockQaVerify
				? TEXT("true")
				: TEXT("false"));
		bSportsbookOfferQa = false;
		bCanonicalHarborFortyPlacementQa = false;
		bCanonicalAutomaticTipoffLockQa = false;
		if (FParse::Param(
				FCommandLine::Get(),
				TEXT("SportsbookOfferAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
	}
}

void AOddsWellPlaceholderCharacter::RunSportsbookOfferQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	SportsbookOfferQaElapsed += DeltaSeconds;
	AOddsWellLocomotionGameMode* GameMode = GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
	if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")) || !GameMode)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_OFFER_QA|result=FAIL|reason=offer_or_map_unavailable|closed=true"));
		bSportsbookOfferQa = false;
		QaExitAt = FPlatformTime::Seconds() + 1.0;
		return;
	}
	if (!GetCharacterMovement()->IsMovingOnGround())
	{
		if (SportsbookOfferQaElapsed > 10.0f)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_OFFER_QA|result=FAIL|reason=spawn_timeout|closed=true"));
			bSportsbookOfferQa = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
		}
		return;
	}
	if (SportsbookOfferQaStage == 0)
	{
		SportsbookOfferQaLedgerEntries = GameMode->GetOddsBucksEntryCount();
		SportsbookOfferQaBalance = GameMode->GetOddsBucksBalance();
		SetActorLocation(SafeSpawnLocation, false, nullptr, ETeleportType::TeleportPhysics);
		ToggleSportsbookOfferPreview();
		if (bSportsbookOfferVisible)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_OFFER_QA|result=FAIL|reason=available_outside_frontage|closed=true"));
			bSportsbookOfferQa = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
			return;
		}
		SetActorLocation(FVector(SportsbookInteractionLocation.X, SportsbookInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
		SportsbookOfferQaStage = 1;
		SportsbookOfferQaElapsed = 0.0f;
		return;
	}
	if (SportsbookOfferQaStage == 1)
	{
		const FString QaLedgerPath = FPaths::Combine(
			FPaths::ProjectSavedDir(),
			TEXT("SaveGames/OddsWellOddsBucksQA.sav"));
		TArray<uint8> BeforeReceiptBytes;
		const FDateTime BeforeReceiptMtime =
			IFileManager::Get().GetTimeStamp(*QaLedgerPath);
		const bool bReadReceiptSource = !bCanonicalSettledLossReceiptQa
			|| FFileHelper::LoadFileToArray(
				BeforeReceiptBytes,
				*QaLedgerPath);
		ToggleSportsbookOfferPreview();
		if (bCanonicalSettledLossReceiptQa)
		{
			const FString ReceiptText = SportsbookSettledLossReceipt
				? BuildCanonicalSettledLossReceiptText(
					*SportsbookSettledLossReceipt)
				: FString();
			const bool bApprovedFinalScore = SportsbookSettledLossReceipt
				&& ((SportsbookSettledLossReceipt->HomeScore == 97
						&& SportsbookSettledLossReceipt->AwayScore == 101)
					|| (SportsbookSettledLossReceipt->HomeScore == 79
						&& SportsbookSettledLossReceipt->AwayScore == 113));
			const bool bExactReceipt = bSportsbookOfferVisible
				&& SportsbookSettledLossReceipt
				&& !SportsbookOfferPreview
				&& !SportsbookCanonicalReceipt
				&& SportsbookSettledLossReceipt->SelectedTeam
					== TEXT("Harbor City Waves")
				&& SportsbookSettledLossReceipt->Stake == 40
				&& bApprovedFinalScore
				&& SportsbookSettledLossReceipt->Winner
					== TEXT("Mesa Vista Sol")
				&& SportsbookSettledLossReceipt->Returned == 0
				&& SportsbookSettledLossReceipt->Net == -40
				&& SportsbookSettledLossReceipt->LedgerEntryCount == 2
				&& SportsbookSettledLossReceipt->CurrentBalance == 60
				&& ReceiptText.Contains(TEXT("BET SETTLED \u2014 LOSS"))
				&& ReceiptText.Contains(FString::Printf(
					TEXT("Final Harbor %d\u2013%d Mesa"),
					SportsbookSettledLossReceipt->HomeScore,
					SportsbookSettledLossReceipt->AwayScore))
				&& ReceiptText.Contains(TEXT("E or ESC: CLOSE"));
			CloseTicketBoothMenu();
			const bool bClosed = !bSportsbookOfferVisible;
			SetActorLocation(
				SafeSpawnLocation,
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			ToggleSportsbookOfferPreview();
			const bool bUnavailableOutsideFrontage =
				!bSportsbookOfferVisible;
			SetActorLocation(
				FVector(
					SportsbookInteractionLocation.X,
					SportsbookInteractionLocation.Y,
					GetActorLocation().Z),
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			ToggleSportsbookOfferPreview();
			TArray<uint8> AfterReceiptBytes;
			const bool bSourceStable = bReadReceiptSource
				&& FFileHelper::LoadFileToArray(
					AfterReceiptBytes,
					*QaLedgerPath)
				&& BeforeReceiptBytes == AfterReceiptBytes
				&& BeforeReceiptMtime
					== IFileManager::Get().GetTimeStamp(*QaLedgerPath);
			const bool bExact = bExactReceipt
				&& bClosed
				&& bUnavailableOutsideFrontage
				&& bSportsbookOfferVisible
				&& SportsbookSettledLossReceipt
				&& bSourceStable
				&& GameMode->GetOddsBucksEntryCount()
					== SportsbookOfferQaLedgerEntries
				&& GameMode->GetOddsBucksEntryCount() == 2
				&& GameMode->GetMatchWinnerRequestCount() == 1
				&& GameMode->GetOddsBucksBalance()
					== SportsbookOfferQaBalance
				&& GameMode->GetOddsBucksBalance() == 60;
			if (!bExact)
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Error,
					TEXT("ODDSWELL_CANONICAL_SETTLED_LOSS_RECEIPT_QA|result=FAIL|reason=receipt_or_invariance_mismatch|unavailable=true"));
				bSportsbookOfferQa = false;
				QaExitAt = FPlatformTime::Seconds() + 1.0;
				return;
			}
			SportsbookOfferQaStage = 2;
			SportsbookOfferQaElapsed = 0.0f;
			return;
		}
		if (bCanonicalBetSlipReviewQa)
		{
			const int64 ExpectedGrossReturns[2][10] = {
				{17, 34, 52, 69, 86, 104, 121, 138, 156, 173},
				{23, 47, 70, 94, 117, 141, 165, 188, 212, 235}};
			FOddsWellMatchWinnerOfferPreview InvalidOffer =
				*SportsbookOfferPreview;
			InvalidOffer.StakeIncrement = 0;
			const bool bInvalidFailsClosed =
				BuildCanonicalBetSlipReviewText(InvalidOffer, 1, 40, 100)
					== TEXT("BET SLIP UNAVAILABLE");
			const bool bPrecedenceExact =
				ShouldShowCanonicalBetSlipReview(true, false, false)
				&& !ShouldShowCanonicalBetSlipReview(true, true, false)
				&& !ShouldShowCanonicalBetSlipReview(true, false, true)
				&& !ShouldShowCanonicalBetSlipReview(false, false, false);
			const bool bInputRoutesExact =
				TicketBoothHomeTeamHitBox != NAME_None
				&& TicketBoothAwayTeamHitBox != NAME_None
				&& TicketBoothStakeDecreaseHitBox != NAME_None
				&& TicketBoothStakeIncreaseHitBox != NAME_None
				&& !KeyLeaguePrevious.IsGamepadKey()
				&& !KeyLeagueNext.IsGamepadKey()
				&& !KeyStakeDecrease.IsGamepadKey()
				&& !KeyStakeIncrease.IsGamepadKey()
				&& KeyControllerTeamPrevious.IsGamepadKey()
				&& KeyControllerTeamNext.IsGamepadKey()
				&& KeyControllerStakeDecrease.IsGamepadKey()
				&& KeyControllerStakeIncrease.IsGamepadKey();
			bool bExactReturns = CanReviewTicketBoothBetSlip()
				&& TicketBoothReviewSelectionIndex == INDEX_NONE
				&& TicketBoothReviewStake == 10;
			for (int32 SelectionIndex = 0;
				bExactReturns && SelectionIndex < 2;
				++SelectionIndex)
			{
				ResetTicketBoothReview();
				SelectTicketBoothReviewTeam(SelectionIndex);
				for (int32 StakeIndex = 0; StakeIndex < 10; ++StakeIndex)
				{
					const FString ReviewText = GetTicketBoothReviewText();
					bExactReturns =
						TicketBoothReviewStake == 10 + StakeIndex * 10
						&& GetTicketBoothReviewGrossReturn()
							== ExpectedGrossReturns[SelectionIndex][StakeIndex]
						&& ReviewText.Contains(
							SportsbookOfferPreview->Selections[SelectionIndex].Team)
						&& ReviewText.Contains(TEXT("REVIEW ONLY \u2014 WAGER NOT PLACED"))
						&& ReviewText.Contains(TEXT("LOCKS AT GAME START"));
					IncreaseTicketBoothReviewStake();
				}
			}
			ResetTicketBoothReview();
			SelectPreviousTicketBoothReviewTeam();
			const bool bPreviousRoute = TicketBoothReviewSelectionIndex == 1;
			SelectNextTicketBoothReviewTeam();
			const bool bNextRoute = TicketBoothReviewSelectionIndex == 0;
			DecreaseTicketBoothReviewStake();
			const bool bMinimumBounded = TicketBoothReviewStake == 10;
			for (int32 Index = 0; Index < 12; ++Index)
			{
				IncreaseTicketBoothReviewStake();
			}
			const bool bMaximumBounded = TicketBoothReviewStake == 100;
			SetTicketBoothMarketPage(1);
			const bool bLaterMarketSafe = SportsbookMarketPage == 1
				&& TicketBoothReviewSelectionIndex == 0
				&& TicketBoothReviewStake == 100;
			SetTicketBoothMarketPage(0);
			CloseTicketBoothMenu();
			const bool bCloseReset = !bSportsbookOfferVisible
				&& TicketBoothReviewSelectionIndex == INDEX_NONE
				&& TicketBoothReviewStake == 10;
			ToggleSportsbookOfferPreview();
			const bool bReopenReset = bSportsbookOfferVisible
				&& TicketBoothReviewSelectionIndex == INDEX_NONE
				&& TicketBoothReviewStake == 10;
			SetActorLocation(
				SafeSpawnLocation,
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			PollSportsbookInteraction();
			const bool bLeaveReset = !bSportsbookOfferVisible
				&& TicketBoothReviewSelectionIndex == INDEX_NONE
				&& TicketBoothReviewStake == 10;
			SetActorLocation(
				FVector(
					SportsbookInteractionLocation.X,
					SportsbookInteractionLocation.Y,
					GetActorLocation().Z),
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			ToggleSportsbookOfferPreview();
			SelectTicketBoothReviewTeam(1);
			for (int32 Index = 0; Index < 3; ++Index)
			{
				IncreaseTicketBoothReviewStake();
			}
			const FString FinalReviewText = GetTicketBoothReviewText();
			const FString LowerReviewText = FinalReviewText.ToLower();
			const bool bExact = bExactReturns
				&& bInvalidFailsClosed
				&& bPrecedenceExact
				&& bInputRoutesExact
				&& bPreviousRoute
				&& bNextRoute
				&& bMinimumBounded
				&& bMaximumBounded
				&& bLaterMarketSafe
				&& bCloseReset
				&& bReopenReset
				&& bLeaveReset
				&& bSportsbookOfferVisible
				&& TicketBoothReviewSelectionIndex == 1
				&& TicketBoothReviewStake == 40
				&& GetTicketBoothReviewGrossReturn() == 94
				&& FinalReviewText.Contains(TEXT("Mesa Vista Sol"))
				&& FinalReviewText.Contains(TEXT("DECIMAL ODDS 2.3577"))
				&& FinalReviewText.Contains(TEXT("STAKE 40 Odds Bucks"))
				&& FinalReviewText.Contains(TEXT("POTENTIAL GROSS RETURN 94 Odds Bucks"))
				&& FinalReviewText.Contains(TEXT("MOUSE:"))
				&& FinalReviewText.Contains(TEXT("KEYBOARD:"))
				&& FinalReviewText.Contains(TEXT("CONTROLLER:"))
				&& !LowerReviewText.Contains(TEXT("confirm"))
				&& !LowerReviewText.Contains(TEXT("submit"))
				&& !LowerReviewText.Contains(TEXT("request"))
				&& !LowerReviewText.Contains(TEXT("debit"))
				&& GameMode->GetOddsBucksEntryCount()
					== SportsbookOfferQaLedgerEntries
				&& GameMode->GetMatchWinnerRequestCount() == 0
				&& GameMode->GetOddsBucksBalance()
					== SportsbookOfferQaBalance;
			if (!bExact)
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Error,
					TEXT("ODDSWELL_CANONICAL_BET_SLIP_REVIEW_QA|result=FAIL|reason=review_or_invariance_mismatch|closed=true"));
				bSportsbookOfferQa = false;
				QaExitAt = FPlatformTime::Seconds() + 1.0;
				return;
			}
			SportsbookOfferQaStage = 2;
			SportsbookOfferQaElapsed = 0.0f;
			return;
		}
		if (bCanonicalPostLockQa)
		{
			const bool bExact =
				bSportsbookOfferVisible
				&& !SportsbookOfferPreview
				&& !SportsbookCanonicalReceipt
				&& GameMode->GetOddsBucksEntryCount() == 2
				&& GameMode->GetMatchWinnerRequestCount() == 1
				&& GameMode->GetOddsBucksBalance() == 60;
			if (!bExact)
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Error,
					TEXT("ODDSWELL_CANONICAL_POST_LOCK_QA|result=FAIL|reason=locked_panel_or_state_mismatch|closed=true"));
				bSportsbookOfferQa = false;
				QaExitAt = FPlatformTime::Seconds() + 1.0;
				return;
			}
			SportsbookOfferQaStage = 2;
			SportsbookOfferQaElapsed = 0.0f;
			return;
		}
		const FString PreviewText = SportsbookOfferPreview
			? BuildOddsWellMatchWinnerOfferPreview(*SportsbookOfferPreview)
			: FString();
		const bool bCanonicalReceiptExact =
			!bCanonicalPendingReceiptQa
			|| (SportsbookCanonicalReceipt
				&& SportsbookCanonicalReceipt->SelectedTeam
					== TEXT("Harbor City Waves")
				&& SportsbookCanonicalReceipt->SelectedWinProbabilityE8
					== 57586693
				&& SportsbookCanonicalReceipt->SelectedDecimalOddsE4 == 17365
				&& SportsbookCanonicalReceipt->Stake == 40
				&& SportsbookCanonicalReceipt->GrossReturn == 69
				&& SportsbookCanonicalReceipt->CurrentBalance == 60
				&& SportsbookCanonicalReceipt->Status
					== FName(TEXT("accepted_pending_lock"))
				&& SportsbookCanonicalReceipt->LockUnixSeconds
					== SportsbookOfferPreview->LockUnix);
		const bool bExact = SportsbookOfferPreview
			&& bSportsbookOfferVisible
			&& PreviewText.Contains(SportsbookOfferPreview->OfferId)
			&& PreviewText.Contains(TEXT("10 -> 17"))
			&& PreviewText.Contains(TEXT("100 -> 235"))
			&& PreviewText.Contains(TEXT("READ ONLY - NO WAGER OR LEDGER CHANGE"))
			&& bCanonicalReceiptExact;
		const bool bUnchanged = bCanonicalPendingReceiptQa
			|| (GameMode->GetOddsBucksEntryCount() == SportsbookOfferQaLedgerEntries
				&& GameMode->GetOddsBucksBalance() == SportsbookOfferQaBalance);
		if (!bExact || !bUnchanged)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_OFFER_QA|result=FAIL|reason=preview_or_ledger_mismatch|closed=true"));
			bSportsbookOfferQa = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
			return;
		}
		if (bCanonicalMissingHeldOpenTipoffQa)
		{
			const int64 TipoffUnix = SportsbookOfferPreview->LockUnix;
			ApplyTicketBoothEvidenceExpiry(
				TipoffUnix,
				EOddsWellCanonicalPendingReceiptResult::Missing,
				bSportsbookOfferVisible,
				SportsbookOfferPreview,
				SportsbookCanonicalReceipt);
			const bool bHeldOpenLocked =
				bSportsbookOfferVisible
				&& !SportsbookOfferPreview
				&& !SportsbookCanonicalReceipt
				&& GameMode->GetOddsBucksEntryCount()
					== SportsbookOfferQaLedgerEntries
				&& GameMode->GetOddsBucksBalance()
					== SportsbookOfferQaBalance;
			if (!bHeldOpenLocked)
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Error,
					TEXT("ODDSWELL_CANONICAL_MISSING_HELD_OPEN_TIPOFF_QA|result=FAIL|reason=expiry_or_ledger_mismatch|closed=true"));
				bSportsbookOfferQa = false;
				QaExitAt = FPlatformTime::Seconds() + 1.0;
				return;
			}
		}
		if (bCanonicalPendingReceiptQa)
		{
			SetTicketBoothMarketPage(1);
			const bool bTabSafe = SportsbookMarketPage == 1;
			SetTicketBoothMarketPage(0);
			CloseTicketBoothMenu();
			SetActorLocation(
				SafeSpawnLocation,
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			ToggleSportsbookOfferPreview();
			const bool bLeaveAndCloseSafe = !bSportsbookOfferVisible;
			SetActorLocation(
				FVector(
					SportsbookInteractionLocation.X,
					SportsbookInteractionLocation.Y,
					GetActorLocation().Z),
				false,
				nullptr,
				ETeleportType::TeleportPhysics);
			ToggleSportsbookOfferPreview();
			if (!bTabSafe
				|| !bLeaveAndCloseSafe
				|| !bSportsbookOfferVisible
				|| !SportsbookCanonicalReceipt)
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Error,
					TEXT("ODDSWELL_CANONICAL_PENDING_RECEIPT_QA|result=FAIL|reason=input_safety_mismatch|closed=true"));
				bSportsbookOfferQa = false;
				QaExitAt = FPlatformTime::Seconds() + 1.0;
				return;
			}
		}
		SportsbookOfferQaStage = 2;
		SportsbookOfferQaElapsed = 0.0f;
		return;
	}
	if (SportsbookOfferQaStage == 2 && SportsbookOfferQaElapsed >= 1.0f)
	{
		if (FParse::Param(FCommandLine::Get(), TEXT("SportsbookOfferQaCapture")))
		{
			FScreenshotRequest::RequestScreenshot(
				bCanonicalBetSlipReviewQa
					? TEXT("Phase1H26Q_CanonicalBetSlipReview.png")
					: (bCanonicalSettledLossReceiptQa
					? TEXT("Phase1H26P_CanonicalSettledLossReceipt.png")
					: (bCanonicalPostLockQa
					? TEXT("Phase1H26G_CanonicalPostLockBooth.png")
					: (bCanonicalMissingHeldOpenTipoffQa
					? TEXT("Phase1H26F_HeldOpenMissingTipoffLocked.png")
					: (bCanonicalPendingReceiptQa
						? TEXT("Phase1H26F_CanonicalPendingReceipt.png")
						: TEXT("Phase1H26D_CanonicalMatchWinnerOffer.png"))))),
				true,
				false);
		}
		if (bCanonicalBetSlipReviewQa)
		{
			SportsbookOfferQaStage = 3;
			SportsbookOfferQaElapsed = 0.0f;
			return;
		}
		if (bCanonicalSettledLossReceiptQa)
		{
			const int32 HomeScore = SportsbookSettledLossReceipt
				? SportsbookSettledLossReceipt->HomeScore
				: 0;
			const int32 AwayScore = SportsbookSettledLossReceipt
				? SportsbookSettledLossReceipt->AwayScore
				: 0;
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_SETTLED_LOSS_RECEIPT_QA|result=PASS|phase=H26AD|cold_restore=true|read_only=true|location=Sportsbook|headline=BET_SETTLED_LOSS|selection=Harbor_City_Waves|stake=40|final_score=%d-%d|winner=Mesa_Vista_Sol|returned=0|net=-40|balance=60|ledger_entries=2|close_instruction=one|view_close_leave_reopen=true|source_bytes_stable=true|source_mtime_stable=true|ids_visible=false|hashes_visible=false|seeds_visible=false|private_athlete_data=false|archive_fallback=false|projection=false|api=false|writer=false|mutation=false"),
				HomeScore,
				AwayScore);
			bSportsbookOfferQa = false;
			if (FParse::Param(
					FCommandLine::Get(),
					TEXT("SportsbookOfferAutoExit")))
			{
				QaExitAt = FPlatformTime::Seconds() + 2.0;
			}
			return;
		}
		if (bCanonicalPostLockQa)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_POST_LOCK_QA|result=PASS|phase=H26G|cold_restore=true|locked_panel=true|offer=false|pending=false|teams=false|prices=false|selection=false|result=false|entries=2|requests=1|locks=1|balance=60|read_only=true|request_api=false|write=false|partial=false"));
			bSportsbookOfferQa = false;
			if (FParse::Param(
					FCommandLine::Get(),
					TEXT("SportsbookOfferAutoExit")))
			{
				QaExitAt = FPlatformTime::Seconds() + 2.0;
			}
			return;
		}
		if (bCanonicalMissingHeldOpenTipoffQa)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_MISSING_HELD_OPEN_TIPOFF_QA|result=PASS|phase=H26F|held_open=true|tipoff=exact|offer_cleared=true|receipt=false|locked_panel=true|teams=false|prices=false|entries_before=%d|entries_after=%d|balance_before=%lld|balance_after=%lld|request_api=false|debit=false|write=false|close_reopen=false"),
				SportsbookOfferQaLedgerEntries,
				GameMode->GetOddsBucksEntryCount(),
				SportsbookOfferQaBalance,
				GameMode->GetOddsBucksBalance());
			bSportsbookOfferQa = false;
			if (FParse::Param(
					FCommandLine::Get(),
					TEXT("SportsbookOfferAutoExit")))
			{
				QaExitAt = FPlatformTime::Seconds() + 2.0;
			}
			return;
		}
		if (bCanonicalPendingReceiptQa)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_PENDING_RECEIPT_QA|result=PASS|phase=H26F|cold_restore=true|read_only=true|canonical=true|selection=Harbor_City_Waves|probability_e8=57586693|odds_e4=17365|stake=40|gross_return=69|balance=60|status=accepted_pending_lock|tipoff=canonical_server_lock|ids_visible=false|cards_interactive=false|open_submit=false|close_submit=false|leave_submit=false|tab_submit=false|cold_submit=false|request_api=false|debit=false|migration=false|write=false|partial=false|locked_claim=false|settled_claim=false"));
			bSportsbookOfferQa = false;
			if (FParse::Param(
					FCommandLine::Get(),
					TEXT("SportsbookOfferAutoExit")))
			{
				QaExitAt = FPlatformTime::Seconds() + 2.0;
			}
			return;
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SPORTSBOOK_OFFER_QA|result=PASS|phase=H26D|location=Sportsbook|interaction=press_e_path|elsewhere=false|read_only=true|canonical=true|archive_fallback=false|timing_authority=server|environment=local_beta|offer_id=%s|season=1|game=1|teams=Harbor_City_Waves_vs_Mesa_Vista_Sol|probabilities_e8=57586693,42413307|odds_e4=17365,23577|stake=10-100|increment=10|lock=server_tipoff|returns=10:17,23;100:173,235|ledger_entries_before=%d|ledger_entries_after=%d|balance_before=%lld|balance_after=%lld|submission=false|selection=false|editor=false|confirm=false|request=false|debit=false|mutation=false"),
			*SportsbookOfferPreview->OfferId,
			SportsbookOfferQaLedgerEntries,
			GameMode->GetOddsBucksEntryCount(),
			SportsbookOfferQaBalance,
			GameMode->GetOddsBucksBalance());
		bSportsbookOfferQa = false;
		if (FParse::Param(FCommandLine::Get(), TEXT("SportsbookOfferAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
	}
	if (SportsbookOfferQaStage == 3 && SportsbookOfferQaElapsed >= 1.0f)
	{
		const int64 TipoffUnix = SportsbookOfferPreview
			? SportsbookOfferPreview->LockUnix
			: 0;
		ApplyTicketBoothEvidenceExpiry(
			TipoffUnix,
			EOddsWellCanonicalPendingReceiptResult::Missing,
			bSportsbookOfferVisible,
			SportsbookOfferPreview,
			SportsbookCanonicalReceipt);
		ResetTicketBoothReview();
		const bool bExact = bCanonicalBetSlipReviewQa
			&& bSportsbookOfferVisible
			&& !SportsbookOfferPreview
			&& !SportsbookCanonicalReceipt
			&& !SportsbookSettledLossReceipt
			&& TicketBoothReviewSelectionIndex == INDEX_NONE
			&& TicketBoothReviewStake == 10
			&& GameMode->GetOddsBucksEntryCount()
				== SportsbookOfferQaLedgerEntries
			&& GameMode->GetMatchWinnerRequestCount() == 0
			&& GameMode->GetOddsBucksBalance()
				== SportsbookOfferQaBalance;
		if (bExact)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_BET_SLIP_REVIEW_QA|result=PASS|phase=H26Q|read_only=true|teams=Harbor_City_Waves,Mesa_Vista_Sol|stakes=10-100|increment=10|returns_exact=true|mouse=true|keyboard=true|controller=true|focus_visible=true|label=REVIEW_ONLY_WAGER_NOT_PLACED|close_reset=true|reopen_reset=true|leave_reset=true|cold_reset=true|later_markets_locked=true|pending_precedence=true|settled_precedence=true|tipoff_clears=true|invalid_reveals=false|confirm=false|submit=false|request=false|debit=false|lock=false|receipt=false|ledger_mutation=false|save_mutation=false|cost_usd=0"));
		}
		else
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Error,
				TEXT("ODDSWELL_CANONICAL_BET_SLIP_REVIEW_QA|result=FAIL|phase=H26Q|reason=tipoff_or_invariance_mismatch"));
		}
		bSportsbookOfferQa = false;
		if (FParse::Param(
				FCommandLine::Get(),
				TEXT("SportsbookOfferAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
	}
}

void AOddsWellPlaceholderCharacter::RunSportsbookWagerQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	SportsbookWagerQaElapsed += DeltaSeconds;
	AOddsWellLocomotionGameMode* GameMode = GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
	if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")) || !GameMode || !SportsbookQaOffer)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_WAGER_QA|result=FAIL|reason=offer_or_map_unavailable"));
		bSportsbookWagerQaAuto = false;
		QaExitAt = FPlatformTime::Seconds() + 1.0;
		return;
	}
	if (!GetCharacterMovement()->IsMovingOnGround())
	{
		if (SportsbookWagerQaElapsed > 10.0f)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_WAGER_QA|result=FAIL|reason=spawn_timeout"));
			bSportsbookWagerQaAuto = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
		}
		return;
	}

	if (bSportsbookWagerQaVerify)
	{
		if (SportsbookWagerQaStage == 0)
		{
			SetActorLocation(FVector(SportsbookInteractionLocation.X, SportsbookInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
			ToggleSportsbookQaWager();
			ServerConfirmSportsbookQaWager(SportsbookQaOffer->HomeTeam, 40);
			int32 Entries = 0;
			int32 Requests = 0;
			int64 Balance = 0;
			FString Error;
			const bool bAudit = GameMode->WasOddsBucksLoadedFromDisk()
				&& GameMode->RunSportsbookQaWagerAudit(Entries, Requests, Balance, Error);
			const bool bPassed = bAudit
				&& bSportsbookQaAccepted
				&& bSportsbookQaDuplicate
				&& Entries == 2
				&& Requests == 1
				&& Balance == 60
				&& GameMode->GetOddsBucksEntryCount() == 2
				&& GameMode->GetMatchWinnerRequestCount() == 1
				&& GameMode->GetOddsBucksBalance() == 60;
			FString CleanupError;
			const bool bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_SPORTSBOOK_WAGER_COLD_QA|result=%s|cold_process_restore=true|exact_retry=duplicate|accepted_at=%lld|lock_unix=%lld|accepted_before_lock=true|rejections=stale,tampered,invalid_team,invalid_stake,late,conflict,completed_h16,insufficient_balance|zero_mutation=true|ledger_entries=%d|requests=%d|balance=%lld|cleanup=%s|detail=%s"),
				bPassed && bCleanup ? TEXT("PASS") : TEXT("FAIL"),
				GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
				SportsbookQaOffer->LockUnixSeconds,
				Entries,
				Requests,
				Balance,
				bCleanup ? TEXT("true") : TEXT("false"),
				bAudit ? *CleanupError : *Error);
			bSportsbookWagerQaAuto = false;
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
		return;
	}

	if (SportsbookWagerQaStage == 0)
	{
		if (GameMode->GetOddsBucksEntryCount() != 1 || GameMode->GetOddsBucksBalance() != 100 || GameMode->GetMatchWinnerRequestCount() != 0)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_WAGER_QA|result=FAIL|reason=job_funded_baseline_mismatch|entries=%d|requests=%d|balance=%lld"), GameMode->GetOddsBucksEntryCount(), GameMode->GetMatchWinnerRequestCount(), GameMode->GetOddsBucksBalance());
			bSportsbookWagerQaAuto = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
			return;
		}
		SetActorLocation(FVector(SportsbookInteractionLocation.X, SportsbookInteractionLocation.Y, GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
		ToggleSportsbookQaWager();
		SelectNextSportsbookQaTeam();
		const bool bAwaySelectable = BuildSportsbookQaWagerText().Contains(FString::Printf(TEXT("TEAM  <  %s  >"), *SportsbookQaOffer->AwayTeam))
			&& BuildSportsbookQaWagerText().Contains(TEXT("22 Odds Bucks"));
		SelectPreviousSportsbookQaTeam();
		for (int32 Index = 0; Index < 12; ++Index)
		{
			IncreaseSportsbookQaStake();
		}
		const bool bMaximumBounded = SportsbookQaStake == 100;
		for (int32 Index = 0; Index < 12; ++Index)
		{
			DecreaseSportsbookQaStake();
		}
		const bool bMinimumBounded = SportsbookQaStake == 10;
		IncreaseSportsbookQaStake();
		IncreaseSportsbookQaStake();
		IncreaseSportsbookQaStake();
		ConfirmSportsbookQaWager();
		const FString ReviewText = BuildSportsbookQaWagerText();
		if (!bSportsbookQaWagerVisible
			|| !bSportsbookQaReviewing
			|| !bAwaySelectable
			|| !bMaximumBounded
			|| !bMinimumBounded
			|| SportsbookQaStake != 40
			|| !ReviewText.Contains(TEXT("EXACT GROSS RETURN\n72 Odds Bucks"))
			|| !ReviewText.Contains(TEXT("PRESS ENTER AGAIN TO CONFIRM")))
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_WAGER_QA|result=FAIL|reason=review_mismatch"));
			bSportsbookWagerQaAuto = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
			return;
		}
		SportsbookWagerQaStage = 1;
		SportsbookWagerQaElapsed = 0.0f;
		return;
	}
	if (SportsbookWagerQaStage == 1 && SportsbookWagerQaElapsed >= 0.25f)
	{
		ConfirmSportsbookQaWager();
		SportsbookWagerQaStage = 2;
		SportsbookWagerQaElapsed = 0.0f;
		return;
	}
	if (SportsbookWagerQaStage == 2 && SportsbookWagerQaElapsed >= 0.5f)
	{
		const FString AcceptedText = BuildSportsbookQaWagerText();
		const bool bPassed = bSportsbookQaAccepted
			&& !bSportsbookQaDuplicate
			&& SportsbookQaAcceptedRequestId == GetOddsWellUpcomingQaMatchWinnerRequestCommandId()
			&& SportsbookQaAcceptedTeam == SportsbookQaOffer->HomeTeam
			&& SportsbookQaStake == 40
			&& SportsbookQaResultingBalance == 60
			&& GameMode->GetOddsBucksEntryCount() == 2
			&& GameMode->GetMatchWinnerRequestCount() == 1
			&& GameMode->GetOddsBucksBalance() == 60
			&& AcceptedText.Contains(TEXT("accepted_pending_lock"))
			&& AcceptedText.Contains(TEXT("No score, winner, replay, result, lock, or settlement was created."));
		if (FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQaCapture")))
		{
			FScreenshotRequest::RequestScreenshot(TEXT("Phase1H17_SportsbookWagerAccepted.png"), true, false);
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SPORTSBOOK_WAGER_QA|result=%s|qa=true|noncanonical=true|location=Sportsbook|review_then_confirm=true|authority=server|atomic=true|request_id=%s|offer_id=%s|team=%s|stake=40|gross_return=72|status=accepted_pending_lock|accepted_at=%lld|lock_unix=%lld|accepted_before_lock=true|ledger_reason=match_winner_stake|ledger_entries=2|requests=1|balance=60|score=false|winner=false|replay=false|result_link=false|hidden_result_state=false|canonical_calendar_unchanged=true"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*SportsbookQaAcceptedRequestId,
			*SportsbookQaOffer->OfferId,
			*SportsbookQaAcceptedTeam,
			GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
			SportsbookQaOffer->LockUnixSeconds);
		bSportsbookWagerQaAuto = false;
		QaExitAt = FPlatformTime::Seconds() + 2.0;
	}
}

void AOddsWellPlaceholderCharacter::RunSportsbookReceiptQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	SportsbookReceiptQaElapsed += DeltaSeconds;
	if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")) || !SportsbookReceipt)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_RECEIPT_QA|result=FAIL|reason=receipt_or_map_unavailable|closed=true"));
		bSportsbookReceiptQaAuto = false;
		QaExitAt = FPlatformTime::Seconds() + 1.0;
		return;
	}
	if (!GetCharacterMovement()->IsMovingOnGround())
	{
		if (SportsbookReceiptQaElapsed > 10.0f)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_RECEIPT_QA|result=FAIL|reason=spawn_timeout|closed=true"));
			bSportsbookReceiptQaAuto = false;
			QaExitAt = FPlatformTime::Seconds() + 1.0;
		}
		return;
	}

	SetActorLocation(
		FVector(SportsbookInteractionLocation.X + SportsbookInteractionRadius * 2.0f, SportsbookInteractionLocation.Y, GetActorLocation().Z),
		false,
		nullptr,
		ETeleportType::TeleportPhysics);
	ToggleSportsbookReceipt();
	const bool bUnavailableOutsideFrontage = !bSportsbookReceiptVisible;
	SetActorLocation(
		FVector(SportsbookInteractionLocation.X, SportsbookInteractionLocation.Y, GetActorLocation().Z),
		false,
		nullptr,
		ETeleportType::TeleportPhysics);
	ToggleSportsbookReceipt();
	const bool bOpenedAtFrontage = bSportsbookReceiptVisible;
	SetActorLocation(
		FVector(SportsbookInteractionLocation.X + SportsbookInteractionRadius * 2.0f, SportsbookInteractionLocation.Y, GetActorLocation().Z),
		false,
		nullptr,
		ETeleportType::TeleportPhysics);
	PollSportsbookInteraction();
	const bool bClosedOnLeave = !bSportsbookReceiptVisible;
	SetActorLocation(
		FVector(SportsbookInteractionLocation.X, SportsbookInteractionLocation.Y, GetActorLocation().Z),
		false,
		nullptr,
		ETeleportType::TeleportPhysics);
	ToggleSportsbookReceipt();

	FOddsWellPendingQaMatchWinnerReceipt RestoredAgain;
	FString Error;
	const bool bRestoredAgain = LoadOddsWellPendingQaMatchWinnerReceipt(RestoredAgain, Error);
	const FString ReceiptText = BuildSportsbookReceiptText();
	const bool bExact = bRestoredAgain
		&& SportsbookReceipt->RequestId == RestoredAgain.RequestId
		&& SportsbookReceipt->OfferId == RestoredAgain.OfferId
		&& SportsbookReceipt->OfferVersion == RestoredAgain.OfferVersion
		&& SportsbookReceipt->SelectedTeam == RestoredAgain.SelectedTeam
		&& SportsbookReceipt->Stake == RestoredAgain.Stake
		&& SportsbookReceipt->AcceptedUnixSeconds == RestoredAgain.AcceptedUnixSeconds
		&& SportsbookReceipt->LockUnixSeconds == RestoredAgain.LockUnixSeconds
		&& SportsbookReceipt->Status == RestoredAgain.Status
		&& SportsbookReceipt->LedgerSequence == RestoredAgain.LedgerSequence
		&& SportsbookReceipt->LedgerDelta == RestoredAgain.LedgerDelta
		&& SportsbookReceipt->LedgerReason == RestoredAgain.LedgerReason
		&& SportsbookReceipt->CurrentBalance == RestoredAgain.CurrentBalance;
	const bool bPassed = bUnavailableOutsideFrontage
		&& bOpenedAtFrontage
		&& bClosedOnLeave
		&& bSportsbookReceiptVisible
		&& bExact
		&& ReceiptText.Contains(SportsbookReceipt->RequestId)
		&& ReceiptText.Contains(SportsbookReceipt->OfferId)
		&& ReceiptText.Contains(SportsbookReceipt->OfferVersion)
		&& ReceiptText.Contains(SportsbookReceipt->SelectedTeam)
		&& ReceiptText.Contains(TEXT("STAKE\n40 Odds Bucks"))
		&& ReceiptText.Contains(TEXT("STATUS  accepted_pending_lock"))
		&& ReceiptText.Contains(TEXT("SEQUENCE  2   DELTA  -40"))
		&& ReceiptText.Contains(TEXT("REASON  match_winner_stake"))
		&& ReceiptText.Contains(TEXT("CURRENT BALANCE\n60 Odds Bucks"))
		&& ReceiptText.Contains(TEXT("No request API, debit, lock, result, or mutation ran in this process."));
	if (FParse::Param(FCommandLine::Get(), TEXT("SportsbookReceiptQaCapture")))
	{
		FScreenshotRequest::RequestScreenshot(TEXT("Phase1H18_PendingMatchWinnerReceipt.png"), true, false);
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_SPORTSBOOK_RECEIPT_QA|result=%s|cold_process_restore=true|press_e_path=true|outside_frontage=false|close_on_leave=true|read_only=true|request_api=false|debit=false|lock=false|result=false|mutation=false|request_id=%s|offer_id=%s|offer_version=%s|team=%s|stake=%lld|accepted_unix=%lld|lock_unix=%lld|status=%s|ledger_sequence=%lld|ledger_delta=%lld|ledger_reason=%s|balance=%lld|detail=%s"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		*SportsbookReceipt->RequestId,
		*SportsbookReceipt->OfferId,
		*SportsbookReceipt->OfferVersion,
		*SportsbookReceipt->SelectedTeam,
		SportsbookReceipt->Stake,
		SportsbookReceipt->AcceptedUnixSeconds,
		SportsbookReceipt->LockUnixSeconds,
		*SportsbookReceipt->Status.ToString(),
		SportsbookReceipt->LedgerSequence,
		SportsbookReceipt->LedgerDelta,
		*SportsbookReceipt->LedgerReason.ToString(),
		SportsbookReceipt->CurrentBalance,
		bRestoredAgain ? TEXT("") : *Error);
	bSportsbookReceiptQaAuto = false;
	QaExitAt = FPlatformTime::Seconds() + 2.0;
}

void AOddsWellPlaceholderCharacter::RunStudioQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	StudioQaElapsed += DeltaSeconds;
	const bool bInSundale = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"));
	const bool bInStudio = GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>() != nullptr;
	if (bStudioPersistenceQaVerify)
	{
		if (bInSundale && GetCharacterMovement()->IsMovingOnGround())
		{
			FOddsWellStudioHomeState Home;
			FString Error;
			const float ReturnDistance = LoadOwnedOddsWellStudio(true, Home, Error)
				? FVector::Dist2D(GetActorLocation(), Home.SundaleReturnLocation)
				: TNumericLimits<float>::Max();
			if (!Home.bOwnsStudio || ReturnDistance > 5.0f || !DeleteOddsWellQaStudioHomeAndVerify(Error))
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_PERSISTENCE_COLD_QA|result=FAIL|reason=%s|return_distance=%.1f"), *Error, ReturnDistance);
				FPlatformMisc::RequestExit(false);
				return;
			}
			bStudioQa = false;
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_PERSISTENCE_COLD_QA|result=PASS|ownership=true|cold_restore=true|return_distance=%.1f|qa_cleanup=true"), ReturnDistance);
			QaExitAt = FPlatformTime::Seconds() + 2.0;
			return;
		}
		if (StudioQaElapsed > 10.0f)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_PERSISTENCE_COLD_QA|result=FAIL|reason=spawn_timeout"));
			FPlatformMisc::RequestExit(false);
		}
		return;
	}
	if (StudioQaProcessStage == 0 && bInSundale && GetCharacterMovement()->IsMovingOnGround())
	{
		if (bStudioPersistenceQa)
		{
			SetActorLocation(GetActorLocation() + FVector(125.0, 75.0, 0.0));
			FString Error;
			if (!SaveOwnedOddsWellStudio(GetActorLocation(), true, Error))
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_PERSISTENCE_QA|result=FAIL|reason=%s"), *Error);
				FPlatformMisc::RequestExit(false);
				return;
			}
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_PERSISTENCE_SAVED|ownership=true|return=%s"), *GetActorLocation().ToCompactString());
		}
		StudioQaProcessStage = 1;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_QA_ENTER|from=SundaleGraybox|private=true|visits=false"));
		UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/Bootstrap")), true, TEXT("game=/Script/OddsWell.OddsWellStudioGameMode"));
		return;
	}
	if (StudioQaProcessStage == 1 && bInStudio)
	{
		if (!bStudioQaInteriorStarted && GetCharacterMovement()->IsMovingOnGround())
		{
			if (bStudioPersistenceQa)
			{
				FOddsWellStudioHomeState Home;
				FString Error;
				if (!LoadOwnedOddsWellStudio(true, Home, Error) || !Home.bOwnsStudio)
				{
					UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_PERSISTENCE_QA|result=FAIL|reason=%s"), *Error);
					FPlatformMisc::RequestExit(false);
					return;
				}
			}
			int32 StructuralSurfaces = 0;
			int32 FurnitureActors = 0;
			for (TActorIterator<AActor> It(GetWorld()); It; ++It)
			{
				StructuralSurfaces += It->ActorHasTag(StudioStructureTag) ? 1 : 0;
				FurnitureActors += It->ActorHasTag(StudioFurnitureTag) ? 1 : 0;
			}
			if (StructuralSurfaces != GetEmptyStudioSurfaces().Num() || FurnitureActors != 0)
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_QA|result=FAIL|reason=interior_contents|structure=%d|furniture=%d"), StructuralSurfaces, FurnitureActors);
				FPlatformMisc::RequestExit(false);
				return;
			}
			bStudioQaInteriorStarted = true;
			StudioQaStartLocation = GetActorLocation();
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_QA_INSIDE|structure=%d|furniture=0|decorations=0|snap_points=0|empty_start=true"), StructuralSurfaces);
		}
		if (bStudioQaInteriorStarted)
		{
			AddMovementInput(FVector::ForwardVector, 1.0f);
			if (FVector::Dist2D(StudioQaStartLocation, GetActorLocation()) >= StudioQaWalkDistance)
			{
				StudioQaProcessStage = 2;
				UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_QA_EXIT|walked=%.1f|to=SundaleGraybox"), FVector::Dist2D(StudioQaStartLocation, GetActorLocation()));
				UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/SundaleGraybox")), true, TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode"));
			}
		}
		return;
	}
	if (StudioQaProcessStage == 2 && bInSundale && GetCharacterMovement()->IsMovingOnGround())
	{
		FOddsWellStudioHomeState Home;
		FString Error;
		const float ReturnDistance = bStudioPersistenceQa && LoadOwnedOddsWellStudio(true, Home, Error)
			? FVector::Dist2D(GetActorLocation(), Home.SundaleReturnLocation)
			: 0.0f;
		if (bStudioPersistenceQa && (!Home.bOwnsStudio || ReturnDistance > 5.0f))
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_PERSISTENCE_QA|result=FAIL|reason=%s|return_distance=%.1f"), *Error, ReturnDistance);
			FPlatformMisc::RequestExit(false);
			return;
		}
		StudioQaProcessStage = 3;
		bStudioQa = false;
		if (bStudioPersistenceQa)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_PERSISTENCE_QA|result=PASS|ownership=true|entered=true|empty=true|exited=true|return_distance=%.1f|disk_record=true|private=true|visits=false"), ReturnDistance);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_QA|result=PASS|entered=true|empty=true|walkable=true|exited=true|returned=SundaleGraybox|private=true|visits=false"));
		}
		if (FParse::Param(FCommandLine::Get(), TEXT("StudioAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
		return;
	}
	if (StudioQaElapsed > 15.0f)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_QA|result=FAIL|reason=transition_timeout|stage=%d|map=%s"), StudioQaProcessStage, *GetWorld()->GetMapName());
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::RunStadiumQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || GetNetMode() != NM_Standalone)
	{
		return;
	}
	StadiumQaElapsed += DeltaSeconds;
	const bool bInSundale = GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox"));
	const bool bInStadium = GetWorld()->GetAuthGameMode<AOddsWellStadiumGameMode>() != nullptr;
	if (StadiumQaProcessStage == 0 && bInSundale && GetCharacterMovement()->IsMovingOnGround())
	{
		StadiumQaProcessStage = 1;
		SetActorLocation(StadiumEntranceThreshold + FVector(0.0, -100.0, SafeSpawnLocation.Z));
		StadiumCityReturnLocation = GetActorLocation();
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_QA_ENTER|from=SundaleGraybox|threshold=%s|sportsbook=separate"), *StadiumEntranceThreshold.ToCompactString());
		UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/Bootstrap")), true, TEXT("game=/Script/OddsWell.OddsWellStadiumGameMode"));
		return;
	}
	if (StadiumQaProcessStage == 1 && bInStadium)
	{
		if (!bStadiumQaInteriorStarted && GetCharacterMovement()->IsMovingOnGround())
		{
			int32 StructuralSurfaces = 0;
			int32 BlockingSurfaces = 0;
			int32 ZoneMarkers = 0;
			for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
			{
				if (It->ActorHasTag(StadiumStructureTag))
				{
					++StructuralSurfaces;
					BlockingSurfaces += It->GetStaticMeshComponent()->GetCollisionResponseToChannel(ECC_Pawn) == ECR_Block ? 1 : 0;
				}
			}
			for (TActorIterator<ATextRenderActor> It(GetWorld()); It; ++It)
			{
				ZoneMarkers += It->ActorHasTag(StadiumZoneTag) ? 1 : 0;
			}
			if (StructuralSurfaces != GetStadiumSurfaces().Num()
				|| BlockingSurfaces != StructuralSurfaces
				|| ZoneMarkers != GetStadiumZones().Num())
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STADIUM_QA|result=FAIL|reason=construction|surfaces=%d|blocking=%d|zones=%d"), StructuralSurfaces, BlockingSurfaces, ZoneMarkers);
				FPlatformMisc::RequestExit(false);
				return;
			}
			bStadiumQaInteriorStarted = true;
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_READY|result=PASS|surfaces=%d|zones=%d|collision=blocking|unbranded=true|team_neutral=true|crowd=0|replay=archived|resimulated=false"), StructuralSurfaces, ZoneMarkers);
		}
		if (!bStadiumQaInteriorStarted)
		{
			return;
		}
		const TArray<FVector>& Waypoints = GetStadiumQaWaypoints();
		if (!Waypoints.IsValidIndex(StadiumQaWaypointIndex))
		{
			return;
		}
		FVector Direction = Waypoints[StadiumQaWaypointIndex] - GetActorLocation();
		Direction.Z = 0.0f;
		if (Direction.Size2D() <= StadiumQaWaypointTolerance)
		{
			++StadiumQaWaypointIndex;
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_QA_ZONE|result=PASS|point=%d/%d|location=%s"), StadiumQaWaypointIndex, Waypoints.Num(), *GetActorLocation().ToCompactString());
			if (StadiumQaWaypointIndex == 4)
			{
				bStadiumQaMarkerReached = true;
				UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_VIEWING_MARKER|result=PASS|label=ARCHIVED_MATCH_PRESENTATION|replay=archived|resimulated=false"));
				if (FParse::Param(FCommandLine::Get(), TEXT("StadiumQaCapture")))
				{
					FScreenshotRequest::RequestScreenshot(TEXT("Phase1F2_StadiumGraybox.png"), true, false);
				}
			}
			if (StadiumQaWaypointIndex == Waypoints.Num())
			{
				if (!bStadiumQaMarkerReached)
				{
					UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STADIUM_QA|result=FAIL|reason=marker_not_reached"));
					FPlatformMisc::RequestExit(false);
					return;
				}
				StadiumQaProcessStage = 2;
				UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/SundaleGraybox")), true, TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode?StadiumReturn=1"));
				return;
			}
		}
		else
		{
			AddMovementInput(Direction.GetSafeNormal(), 1.0f);
		}
	}
	else if (StadiumQaProcessStage == 2 && bInSundale && GetCharacterMovement()->IsMovingOnGround())
	{
		const float ReturnDistance = FVector::Dist2D(GetActorLocation(), StadiumCityReturnLocation);
		StadiumQaProcessStage = 3;
		bStadiumQa = false;
		if (ReturnDistance > 5.0f)
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STADIUM_QA|result=FAIL|reason=return_threshold|distance=%.1f"), ReturnDistance);
			FPlatformMisc::RequestExit(false);
			return;
		}
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_QA|result=PASS|entered=true|walked_to_marker=true|exited=true|return_distance=%.1f|zones=5|sportsbook=separate|replay=archived|resimulated=false|wagering=false"), ReturnDistance);
		if (FParse::Param(FCommandLine::Get(), TEXT("StadiumAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
		return;
	}
	if (StadiumQaElapsed > 45.0f)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STADIUM_QA|result=FAIL|reason=transition_timeout|stage=%d|map=%s"), StadiumQaProcessStage, *GetWorld()->GetMapName());
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::RunCameraOrbitQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || !Controller)
	{
		return;
	}
	CameraOrbitQaElapsed += DeltaSeconds;
	const float CurrentYaw = Controller->GetControlRotation().Yaw;
	if (!bCameraOrbitQaStarted)
	{
		bCameraOrbitQaStarted = true;
		CameraOrbitQaPreviousYaw = CurrentYaw;
		CameraOrbitQaStartLocation = GetActorLocation();
	}
	else
	{
		CameraOrbitQaSweep += FMath::Abs(FMath::FindDeltaAngleDegrees(CameraOrbitQaPreviousYaw, CurrentYaw));
		CameraOrbitQaPreviousYaw = CurrentYaw;
	}
	LookYaw(4.0f);
	if (CameraOrbitQaSweep >= 370.0f)
	{
		const float Drift = FVector::Dist2D(CameraOrbitQaStartLocation, GetActorLocation());
		const bool bPassed = Drift <= 5.0f;
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CAMERA_ORBIT_QA|result=%s|sweep=%.1f|full_orbit=true|player_drift=%.1f|mouse_axis=true|map=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			CameraOrbitQaSweep,
			Drift,
			*GetWorld()->GetMapName());
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		bCameraOrbitQa = false;
		if (FParse::Param(FCommandLine::Get(), TEXT("CameraOrbitAutoExit")))
		{
			QaExitAt = FPlatformTime::Seconds() + 2.0;
		}
		return;
	}
	if (CameraOrbitQaElapsed > 5.0f)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_CAMERA_ORBIT_QA|result=FAIL|reason=timeout|sweep=%.1f|map=%s"), CameraOrbitQaSweep, *GetWorld()->GetMapName());
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::RunSharedCityQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || SharedCityPlayerNumber < 1)
	{
		return;
	}
	SharedCityQaElapsed += DeltaSeconds;
	int32 VisiblePlayers = 0;
	int32 SubmittedAppearances = 0;
	int32 OtherPlayerNumber = 0;
	AOddsWellPlaceholderCharacter* OtherPlayer = nullptr;
	for (TActorIterator<AOddsWellPlaceholderCharacter> It(GetWorld()); It; ++It)
	{
		if (It->SharedCityPlayerNumber > 0 && It->SharedCityNameplate && It->SharedCityNameplate->IsVisible())
		{
			++VisiblePlayers;
			if (It->HasValidSharedCityAppearance() && It->HasSubmittedSharedCityAppearance())
			{
				++SubmittedAppearances;
			}
			if (*It != this)
			{
				OtherPlayerNumber = It->SharedCityPlayerNumber;
				OtherPlayer = *It;
			}
		}
	}
	if (bSharedCityCapacityQa
		&& !bSharedCityCapacityLogged
		&& VisiblePlayers >= SharedCityQaTargetClients
		&& SubmittedAppearances >= SharedCityQaTargetClients)
	{
		bSharedCityCapacityLogged = true;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_CAPACITY_VISIBLE|local=Player_%d|clients=%d|visible=%d|submitted_appearances=%d|names=true|pawn_collision=ignore"),
			SharedCityPlayerNumber,
			SharedCityQaTargetClients,
			VisiblePlayers,
			SubmittedAppearances);
		if (GetNetMode() == NM_Client && FParse::Param(FCommandLine::Get(), TEXT("SharedCityCapacityAutoExit")))
		{
			SharedCityQaExitAt = FPlatformTime::Seconds() + 3.0;
		}
	}
	if (!bSharedCityQaVisibleLogged && VisiblePlayers >= 2 && OtherPlayerNumber > 0)
	{
		bSharedCityQaVisibleLogged = true;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_VISIBLE|local=Player_%d|other=Player_%d|actors=%d|names=true|pawn_collision=ignore"),
			SharedCityPlayerNumber,
			OtherPlayerNumber,
			VisiblePlayers);
	}
	if (!bSharedCityQaAppearanceLogged
		&& bSharedCityQaVisibleLogged
		&& OtherPlayer
		&& HasValidSharedCityAppearance()
		&& OtherPlayer->HasValidSharedCityAppearance()
		&& HasSubmittedSharedCityAppearance()
		&& OtherPlayer->HasSubmittedSharedCityAppearance())
	{
		bSharedCityQaAppearanceLogged = true;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_APPEARANCE|local=Player_%d|local_preset=%s|local_top=%s|local_bottom=%s|other=Player_%d|other_preset=%s|other_top=%s|other_bottom=%s|agreement=true"),
			SharedCityPlayerNumber,
			*SharedCityAppearance.PresetId.ToString(),
			*SharedCityAppearance.TopItemId.ToString(),
			*SharedCityAppearance.BottomItemId.ToString(),
			OtherPlayerNumber,
			*OtherPlayer->SharedCityAppearance.PresetId.ToString(),
			*OtherPlayer->SharedCityAppearance.TopItemId.ToString(),
			*OtherPlayer->SharedCityAppearance.BottomItemId.ToString());
		if (GetNetMode() == NM_Client
			&& bAppearanceQa
			&& FParse::Param(FCommandLine::Get(), TEXT("SharedCityReconnectCleanup")))
		{
			FString Error;
			const bool bClean = DeleteOddsWellQaAppearanceAndVerify(Error);
			if (bClean)
			{
				UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_RECONNECT_CLEANUP|result=PASS|slot=qa|exists=false"));
			}
			else
			{
				UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SHARED_CITY_RECONNECT_CLEANUP|result=FAIL|slot=qa|reason=%s"), *Error);
			}
		}
		if (GetNetMode() == NM_Client && FParse::Param(FCommandLine::Get(), TEXT("SharedCityAutoExit")))
		{
			SharedCityQaExitAt = FPlatformTime::Seconds() + 3.0;
		}
	}
	if (GetNetMode() == NM_Client && bSharedCityQaVisibleLogged)
	{
		AddMovementInput(FVector::ForwardVector, 1.0f);
	}
	if (SharedCityQaExitAt > 0.0 && FPlatformTime::Seconds() >= SharedCityQaExitAt)
	{
		SharedCityQaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::PollKeyboardMovement()
{
	const APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController)
	{
		return;
	}
	MoveForward((PlayerController->IsInputKeyDown(KeyForward) ? 1.0f : 0.0f) - (PlayerController->IsInputKeyDown(KeyBackward) ? 1.0f : 0.0f));
	MoveRight((PlayerController->IsInputKeyDown(KeyRight) ? 1.0f : 0.0f) - (PlayerController->IsInputKeyDown(KeyLeft) ? 1.0f : 0.0f));
}

void AOddsWellPlaceholderCharacter::MoveForward(const float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
	}
}

void AOddsWellPlaceholderCharacter::MoveRight(const float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
	}
}

void AOddsWellPlaceholderCharacter::LookYaw(const float Value) { AddControllerYawInput(Value); }
void AOddsWellPlaceholderCharacter::LookPitchMouse(const float Value) { AddControllerPitchInput(-Value); }
void AOddsWellPlaceholderCharacter::LookPitchController(const float Value) { AddControllerPitchInput(Value); }
void AOddsWellPlaceholderCharacter::StartRun() { GetCharacterMovement()->MaxWalkSpeed = RunSpeed; }
void AOddsWellPlaceholderCharacter::StopRun() { GetCharacterMovement()->MaxWalkSpeed = WalkSpeed; }
void AOddsWellPlaceholderCharacter::StartJump()
{
	if (!bSportsbookOfferVisible)
	{
		Jump();
	}
}
void AOddsWellPlaceholderCharacter::StopJump() { StopJumping(); }

bool AOddsWellPlaceholderCharacter::ApplySavedOrFallbackAppearance()
{
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Source;
	FString Error;
	if (!ResolveLocalAppearance(Appearance, Source, Error) || !Appearance.Preset)
	{
		ReportAppearanceError(Error.IsEmpty() ? TEXT("No valid local or fallback appearance is available.") : Error);
		return false;
	}
	if (!Error.IsEmpty())
	{
		UE_LOG(LogOddsWellLocomotion, Warning, TEXT("ODDSWELL_APPEARANCE_FALLBACK|source=%s|reason=%s|record_preserved=true"), *Source, *Error);
	}
	return ApplyResolvedAppearance(Appearance, Source);
}

bool AOddsWellPlaceholderCharacter::ResolveLocalAppearance(
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutSource,
	FString& OutError) const
{
	FString QaPresetId;
	if (bSharedCityQa && FParse::Value(FCommandLine::Get(), TEXT("SharedCityQaPreset="), QaPresetId))
	{
		const FOddsWellCharacterPreset* Preset = FindOddsWellCharacterPreset(FName(*QaPresetId));
		if (!Preset || Preset->EquippedItemIds.Num() != 2)
		{
			OutError = FString::Printf(TEXT("Unsupported shared-city QA preset: %s"), *QaPresetId);
			return false;
		}
		OutSource = TEXT("shared_city_qa");
		return ValidateOddsWellCharacterAppearanceIds(
			Preset->Id,
			Preset->EquippedItemIds[0],
			Preset->EquippedItemIds[1],
			OutAppearance,
			OutError);
	}
	return LoadOddsWellCharacterAppearance(bAppearanceQa, OutAppearance, OutSource, OutError);
}

bool AOddsWellPlaceholderCharacter::ApplyResolvedAppearance(
	const FOddsWellResolvedCharacterAppearance& Appearance,
	const FString& Source)
{
	FString Error;
	if (!PrimitiveSkinMaterial)
	{
		ReportAppearanceError(TEXT("The primitive skin material is unavailable."));
		return false;
	}
	StarterOutfitState.Reset();
	if (!StarterOutfitState.Equip(Appearance.TopItemId, EOddsWellStarterEquipmentSlot::Top, Error)
		|| !StarterOutfitState.Equip(Appearance.BottomItemId, EOddsWellStarterEquipmentSlot::Bottom, Error)
		|| !StarterOutfitState.ValidateComplete(Error))
	{
		ReportOutfitError(Error);
		return false;
	}
	PrimitiveSkinMaterial->SetVectorParameterValue(TEXT("Color"), FLinearColor::FromSRGBColor(Appearance.Preset->SkinTone));
	SyncOutfitComponents();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_APPEARANCE_READY|schema=1|preset=%s|top=%s|bottom=%s|source=%s|skin=%s|presentation=%s|slot=%s"),
		*Appearance.Preset->Id.ToString(),
		*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).ToString(),
		*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString(),
		*Source,
		*Appearance.Preset->SkinTone.ToHex(),
		Appearance.Preset->Presentation == EOddsWellCharacterPresentation::Masculine ? TEXT("masculine") : TEXT("feminine"),
		bAppearanceQa ? TEXT("qa") : TEXT("production"));
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_OUTFIT_READY|top=%s|slot=top|bottom=%s|slot=bottom|replaceable=true"),
		*Appearance.TopItemId.ToString(),
		*Appearance.BottomItemId.ToString());
	return true;
}

bool AOddsWellPlaceholderCharacter::ApplySharedCityAppearance(const FString& Source)
{
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Error;
	if (!ValidateOddsWellCharacterAppearanceIds(
		SharedCityAppearance.PresetId,
		SharedCityAppearance.TopItemId,
		SharedCityAppearance.BottomItemId,
		Appearance,
		Error))
	{
		ReportAppearanceError(Error);
		return false;
	}
	return ApplyResolvedAppearance(Appearance, Source);
}

void AOddsWellPlaceholderCharacter::SubmitLocalSharedCityAppearance()
{
	if (bSharedCityAppearanceSubmitted)
	{
		return;
	}
	if (bAppearanceQa && FParse::Param(FCommandLine::Get(), TEXT("SharedCityReconnectSeed")))
	{
		FString QaPresetId;
		FString Error;
		if (!FParse::Value(FCommandLine::Get(), TEXT("SharedCityQaPreset="), QaPresetId)
			|| !SaveOddsWellCharacterAppearance(FName(*QaPresetId), true, Error))
		{
			ReportAppearanceError(Error.IsEmpty() ? TEXT("Reconnect QA requires a valid SharedCityQaPreset.") : Error);
			return;
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_RECONNECT_SEED|result=PASS|preset=%s|slot=qa"),
			*QaPresetId);
	}
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Source;
	FString Error;
	if (!ResolveLocalAppearance(Appearance, Source, Error) || !Appearance.Preset)
	{
		ReportAppearanceError(Error.IsEmpty() ? TEXT("No valid local shared-city appearance is available.") : Error);
		return;
	}
	if (!Error.IsEmpty())
	{
		UE_LOG(LogOddsWellLocomotion, Warning, TEXT("ODDSWELL_APPEARANCE_FALLBACK|source=%s|reason=%s|record_preserved=true"), *Source, *Error);
	}
	if (!ApplyResolvedAppearance(Appearance, Source))
	{
		return;
	}
	bSharedCityAppearanceSubmitted = true;
	if (HasAuthority())
	{
		SetAuthoritativeSharedCityAppearance(Appearance.Preset->Id, Appearance.TopItemId, Appearance.BottomItemId, true, Source);
	}
	else
	{
		ServerSetSharedCityAppearance(Appearance.Preset->Id, Appearance.TopItemId, Appearance.BottomItemId);
	}
}

void AOddsWellPlaceholderCharacter::ServerSetSharedCityAppearance_Implementation(
	const FName PresetId,
	const FName TopItemId,
	const FName BottomItemId)
{
	SetAuthoritativeSharedCityAppearance(PresetId, TopItemId, BottomItemId, true, TEXT("client_rpc"));
}

void AOddsWellPlaceholderCharacter::SetAuthoritativeSharedCityAppearance(
	const FName PresetId,
	const FName TopItemId,
	const FName BottomItemId,
	const bool bOwnerSubmitted,
	const FString& Source)
{
	if (!HasAuthority())
	{
		return;
	}
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Error;
	if (!ValidateOddsWellCharacterAppearanceIds(PresetId, TopItemId, BottomItemId, Appearance, Error))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SHARED_CITY_APPEARANCE_REJECTED|player=%d|reason=%s"), SharedCityPlayerNumber, *Error);
		return;
	}
	SharedCityAppearance.PresetId = PresetId;
	SharedCityAppearance.TopItemId = TopItemId;
	SharedCityAppearance.BottomItemId = BottomItemId;
	SharedCityAppearance.bOwnerSubmitted = bOwnerSubmitted;
	ApplyResolvedAppearance(Appearance, Source);
	ForceNetUpdate();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_SHARED_CITY_APPEARANCE_ACCEPTED|player=%d|preset=%s|top=%s|bottom=%s|owner_submitted=%s|source=%s"),
		SharedCityPlayerNumber,
		*PresetId.ToString(),
		*TopItemId.ToString(),
		*BottomItemId.ToString(),
		bOwnerSubmitted ? TEXT("true") : TEXT("false"),
		*Source);
}

void AOddsWellPlaceholderCharacter::SyncOutfitComponents()
{
	StarterOutfitTop->SetVisibility(!StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).IsNone(), true);
	StarterOutfitBottom->SetVisibility(!StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).IsNone(), true);
}

void AOddsWellPlaceholderCharacter::RunOutfitQa(const float DeltaSeconds)
{
	OutfitQaElapsed += DeltaSeconds;
	FString Error;
	if (OutfitQaStage == 0 && OutfitQaElapsed >= 0.75f)
	{
		if (!StarterOutfitState.Unequip(EOddsWellStarterEquipmentSlot::Top, Error))
		{
			ReportOutfitError(Error);
			bOutfitQaEnabled = false;
			return;
		}
		SyncOutfitComponents();
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_OUTFIT_UNEQUIP|slot=top|top=none|bottom=%s|base_body=true"), *StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString());
		OutfitQaStage = 1;
	}
	else if (OutfitQaStage == 1 && OutfitQaElapsed >= 1.75f)
	{
		FName TopId;
		FName BottomId;
		if (!GetOddsWellStarterEquipmentIds(TopId, BottomId, Error)
			|| !StarterOutfitState.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error)
			|| !StarterOutfitState.ValidateComplete(Error))
		{
			ReportOutfitError(Error);
			bOutfitQaEnabled = false;
			return;
		}
		SyncOutfitComponents();
		const bool bPassed = PrimitiveBody->IsVisible()
			&& StarterOutfitTop->IsVisible()
			&& StarterOutfitBottom->IsVisible()
			&& GetCharacterMovement()->MaxWalkSpeed == WalkSpeed
			&& RunSpeed == 520.0f
			&& GetCharacterMovement()->JumpZVelocity == JumpVelocity;
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_OUTFIT_QA|result=%s|top=%s|bottom=%s|replaceable=true|base_body=%s|top_component=%s|top_visible=%s|bottom_component=%s|bottom_visible=%s|walk=%.0f|run=%.0f|jump=%.0f"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).ToString(),
			*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString(),
			PrimitiveBody->IsVisible() ? TEXT("true") : TEXT("false"),
			*StarterOutfitTop->GetFName().ToString(),
			StarterOutfitTop->IsVisible() ? TEXT("true") : TEXT("false"),
			*StarterOutfitBottom->GetFName().ToString(),
			StarterOutfitBottom->IsVisible() ? TEXT("true") : TEXT("false"),
			WalkSpeed,
			RunSpeed,
			JumpVelocity);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		bOutfitQaEnabled = false;
		OutfitQaStage = 2;
	}
}

void AOddsWellPlaceholderCharacter::ReportOutfitError(const FString& Error) const
{
	UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_OUTFIT_ERROR|%s"), *Error);
}

void AOddsWellPlaceholderCharacter::ReportAppearanceError(const FString& Error) const
{
	UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_APPEARANCE_ERROR|%s"), *Error);
}

void AOddsWellPlaceholderCharacter::RunQa(const float DeltaSeconds)
{
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	if (!bQaStarted)
	{
		QaElapsed += DeltaSeconds;
		if (!Movement->IsMovingOnGround())
		{
			if (QaElapsed > 5.0f)
			{
				QaStartLocation = GetActorLocation();
				QaMaxZ = QaStartLocation.Z;
				FinishQa(false);
			}
			return;
		}
		bQaStarted = true;
		QaElapsed = 0.0f;
		QaStartLocation = GetActorLocation();
		QaMaxZ = QaStartLocation.Z;
		if (Controller)
		{
			Controller->SetControlRotation(FRotator(-12.0f, 0.0f, 0.0f));
		}
		QaStartYaw = Controller ? Controller->GetControlRotation().Yaw : 0.0f;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_LOCOMOTION_QA_START|location=%s|yaw=%.1f"), *QaStartLocation.ToCompactString(), QaStartYaw);
	}

	if (bQaFinished)
	{
		return;
	}
	QaElapsed += DeltaSeconds;
	QaMaxZ = FMath::Max(QaMaxZ, GetActorLocation().Z);
	const float HorizontalSpeed = GetVelocity().Size2D();
	if (QaElapsed < 1.5f)
	{
		StopRun();
		MoveForward(1.0f);
		QaWalkPeak = FMath::Max(QaWalkPeak, HorizontalSpeed);
	}
	else if (QaElapsed < 2.0f)
	{
		if (Controller)
		{
			FRotator View = Controller->GetControlRotation();
			View.Yaw += (QaStartYaw > 0.0f ? -70.0f : 70.0f) * DeltaSeconds;
			View.Pitch = FMath::Clamp(View.Pitch + 20.0f * DeltaSeconds, CameraPitchMin, CameraPitchMax);
			Controller->SetControlRotation(View);
		}
	}
	else if (QaElapsed < 3.5f)
	{
		StartRun();
		MoveForward(1.0f);
		QaRunPeak = FMath::Max(QaRunPeak, HorizontalSpeed);
	}
	else
	{
		StopRun();
		if (!bQaJumpIssued)
		{
			bQaJumpIssued = true;
			Jump();
		}
		if (!Movement->IsMovingOnGround())
		{
			MoveForward(1.0f);
		}
		else if (QaElapsed > 3.7f && QaMaxZ - QaStartLocation.Z > 50.0f)
		{
			const float YawDelta = Controller ? FMath::Abs(FMath::FindDeltaAngleDegrees(QaStartYaw, Controller->GetControlRotation().Yaw)) : 0.0f;
			const bool bFloorBlocking = Movement->CurrentFloor.bBlockingHit;
			const bool bPassed = FVector::Dist2D(QaStartLocation, GetActorLocation()) > 100.0f
				&& QaRunPeak > QaWalkPeak + 50.0f
				&& QaMaxZ - QaStartLocation.Z > 50.0f
				&& FMath::Abs(GetActorLocation().Z - QaStartLocation.Z) < 25.0f
				&& YawDelta > 10.0f
				&& bFloorBlocking
				&& FMath::IsNearlyEqual(Movement->MaxWalkSpeed, WalkSpeed);
			FinishQa(bPassed);
		}
	}

	if (QaElapsed > 8.0f && !bQaFinished)
	{
		FinishQa(false);
	}
}

void AOddsWellPlaceholderCharacter::FinishQa(const bool bPassed)
{
	bQaFinished = true;
	const float YawDelta = Controller ? FMath::Abs(FMath::FindDeltaAngleDegrees(QaStartYaw, Controller->GetControlRotation().Yaw)) : 0.0f;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_LOCOMOTION_QA|result=%s|start=%s|end=%s|walk_peak=%.1f|run_peak=%.1f|walk_limit=%.0f|run_limit=%.0f|max_jump=%.1f|landed=%s|floor_blocking=%s|yaw_delta=%.1f"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		*QaStartLocation.ToCompactString(),
		*GetActorLocation().ToCompactString(),
		QaWalkPeak,
		QaRunPeak,
		WalkSpeed,
		RunSpeed,
		QaMaxZ - QaStartLocation.Z,
		GetCharacterMovement()->IsMovingOnGround() ? TEXT("true") : TEXT("false"),
		GetCharacterMovement()->CurrentFloor.bBlockingHit ? TEXT("true") : TEXT("false"),
		YawDelta);
	if (bPassed)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	if (bAppearanceQaCleanup)
	{
		FString Error;
		const bool bClean = bAppearanceQa && DeleteOddsWellQaAppearanceAndVerify(Error);
		if (bClean)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_APPEARANCE_QA_CLEANUP|result=PASS|slot=qa|exists=false"));
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_APPEARANCE_QA_CLEANUP|result=FAIL|slot=%s|reason=%s"), bAppearanceQa ? TEXT("qa") : TEXT("production"), *Error);
		}
		bAppearanceQaCleanup = false;
	}
	if (bQaAutoExit)
	{
		QaExitAt = FPlatformTime::Seconds() + 12.0;
	}
}

void AOddsWellPlaceholderCharacter::RunSundaleRouteQa(const float DeltaSeconds)
{
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	if (bSundaleRouteFinished)
	{
		return;
	}
	if (!bSundaleRouteStarted)
	{
		SundaleRouteElapsed += DeltaSeconds;
		if (!Movement->IsMovingOnGround())
		{
			if (SundaleRouteElapsed > 10.0f)
			{
				FinishSundaleRouteQa(false);
			}
			return;
		}
		if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")))
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SUNDALE_ROUTE_ERROR|reason=wrong_map|map=%s"), *GetWorld()->GetMapName());
			FinishSundaleRouteQa(false);
			return;
		}
		bSundaleRouteStarted = true;
		SundaleRouteElapsed = 0.0f;
		SundaleRouteStart = GetActorLocation();
		SundalePreviousLocation = SundaleRouteStart;
		SundaleMinZ = SundaleRouteStart.Z;
		SundaleMaxZ = SundaleRouteStart.Z;
		if (bSundaleRouteRun)
		{
			StartRun();
		}
		else
		{
			StopRun();
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SUNDALE_ROUTE_START|mode=%s|map=%s|start=%s|planned_distance=%.0f"),
			bSundaleRouteRun ? TEXT("run") : TEXT("walk"),
			*GetWorld()->GetMapName(),
			*SundaleRouteStart.ToCompactString(),
			SundaleRouteDistance);
		return;
	}
	SundaleRouteElapsed += DeltaSeconds;
	SundaleSegmentElapsed += DeltaSeconds;
	const FVector CurrentLocation = GetActorLocation();
	SundaleTravelDistance += FVector::Dist2D(SundalePreviousLocation, CurrentLocation);
	SundalePreviousLocation = CurrentLocation;
	SundaleMinZ = FMath::Min(SundaleMinZ, CurrentLocation.Z);
	SundaleMaxZ = FMath::Max(SundaleMaxZ, CurrentLocation.Z);

	const TArray<FVector>& Waypoints = GetSundaleRouteWaypoints();
	if (!Waypoints.IsValidIndex(SundaleRouteIndex))
	{
		FinishSundaleRouteQa(true);
		return;
	}

	FVector Direction = Waypoints[SundaleRouteIndex] - CurrentLocation;
	Direction.Z = 0.0f;
	if (Direction.Size2D() <= SundaleWaypointTolerance)
	{
		const TArray<FString>& Labels = GetSundaleRouteWaypointLabels();
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SUNDALE_ROUTE_POINT|index=%d|name=%s|segment_seconds=%.3f|location=%s"),
			SundaleRouteIndex + 1,
			*Labels[SundaleRouteIndex],
			SundaleSegmentElapsed,
			*CurrentLocation.ToCompactString());
		++SundaleRouteIndex;
		SundaleSegmentElapsed = 0.0f;
		if (SundaleRouteIndex == Waypoints.Num())
		{
			FinishSundaleRouteQa(true);
		}
		return;
	}

	AddMovementInput(Direction.GetSafeNormal(), 1.0f);
	const float PlannedSeconds = SundaleRouteDistance / (bSundaleRouteRun ? RunSpeed : WalkSpeed);
	if (SundaleRouteElapsed > PlannedSeconds * 1.6f + 10.0f)
	{
		FinishSundaleRouteQa(false);
	}
}

void AOddsWellPlaceholderCharacter::FinishSundaleRouteQa(const bool bPassed)
{
	if (bSundaleRouteFinished)
	{
		return;
	}
	bSundaleRouteFinished = true;
	StopRun();
	const bool bAllPoints = SundaleRouteIndex == GetSundaleRouteWaypoints().Num();
	const bool bReturnedHome = FVector::Dist2D(SundaleRouteStart, GetActorLocation()) <= 150.0f;
	const bool bDistancePlausible = SundaleTravelDistance >= SundaleRouteDistance * 0.96f
		&& SundaleTravelDistance <= SundaleRouteDistance * 1.04f;
	const bool bFloorBlocking = GetCharacterMovement()->CurrentFloor.bBlockingHit;
	const bool bVerticalStable = SundaleMaxZ - SundaleMinZ <= 100.0f;
	const bool bFinalPass = bPassed && bAllPoints && bReturnedHome && bDistancePlausible
		&& GetCharacterMovement()->IsMovingOnGround() && bFloorBlocking && bVerticalStable;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_SUNDALE_ROUTE_QA|result=%s|mode=%s|seconds=%.3f|planned_distance=%.0f|traveled_distance=%.1f|points=%d/%d|returned_home=%s|landed=%s|floor_blocking=%s|vertical_range=%.1f"),
		bFinalPass ? TEXT("PASS") : TEXT("FAIL"),
		bSundaleRouteRun ? TEXT("run") : TEXT("walk"),
		SundaleRouteElapsed,
		SundaleRouteDistance,
		SundaleTravelDistance,
		SundaleRouteIndex,
		GetSundaleRouteWaypoints().Num(),
		bReturnedHome ? TEXT("true") : TEXT("false"),
		GetCharacterMovement()->IsMovingOnGround() ? TEXT("true") : TEXT("false"),
		bFloorBlocking ? TEXT("true") : TEXT("false"),
		SundaleMaxZ - SundaleMinZ);
	if (bFinalPass)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	if (bQaAutoExit)
	{
		QaExitAt = FPlatformTime::Seconds() + 2.0;
	}
}

AOddsWellPlaceholderCharacter* AOddsWellSportsbookHUD::GetOddsWellCharacter() const
{
	const APlayerController* PlayerController = GetOwningPlayerController();
	return PlayerController ? Cast<AOddsWellPlaceholderCharacter>(PlayerController->GetPawn()) : nullptr;
}

void AOddsWellSportsbookHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas)
	{
		return;
	}
	AOddsWellPlaceholderCharacter* Character = GetOddsWellCharacter();
	if (!Character)
	{
		return;
	}
	if (Character->IsTicketBoothMenuVisible())
	{
		if (const FOddsWellCanonicalSettledLossReceipt* Receipt =
			Character->GetTicketBoothSettledLossReceipt())
		{
			DrawTicketBoothSettledLossReceipt(*Receipt);
		}
		else if (const FOddsWellMatchWinnerOfferPreview* Offer = Character->GetTicketBoothOffer())
		{
			DrawTicketBoothMenu(*Character, *Offer);
		}
		else
		{
			DrawTicketBoothUnavailableMenu();
		}
	}
	else if (Character->IsTicketBoothPromptVisible())
	{
		DrawTicketBoothPrompt();
	}
	else
	{
		DrawSettledLossHandoffCue(*Character);
	}
}

void AOddsWellSportsbookHUD::DrawSettledLossHandoffCue(
	const AOddsWellPlaceholderCharacter& Character)
{
	FString Cue;
	if (!BuildSettledLossHandoffCue(
			Character.GetTicketBoothSettledLossReceipt() != nullptr,
			GetWorld()->GetMapName(),
			Character.GetActorLocation(),
			Character.GetControlRotation().Yaw,
			Character.IsTicketBoothMenuVisible(),
			GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>() != nullptr,
			GetWorld()->GetAuthGameMode<AOddsWellStadiumGameMode>() != nullptr,
			Cue))
	{
		return;
	}
	const float Width = FMath::Min(850.0f, Canvas->SizeX - 32.0f);
	const float Height = 52.0f;
	const float X = (Canvas->SizeX - Width) * 0.5f;
	const float Y = 24.0f;
	DrawRect(FLinearColor(0.025f, 0.055f, 0.08f, 0.94f), X, Y, Width, Height);
	DrawRect(FLinearColor(0.96f, 0.78f, 0.30f, 1.0f), X, Y, Width, 4.0f);
	DrawText(Cue, FLinearColor::White, X + 20.0f, Y + 16.0f, nullptr, 1.0f);
}

void AOddsWellSportsbookHUD::DrawTicketBoothPrompt()
{
	const float Width = FMath::Min(430.0f, Canvas->SizeX - 32.0f);
	const float Height = 58.0f;
	const float X = (Canvas->SizeX - Width) * 0.5f;
	const float Y = Canvas->SizeY - Height - 42.0f;
	DrawRect(FLinearColor(0.025f, 0.055f, 0.08f, 0.94f), X, Y, Width, Height);
	DrawRect(FLinearColor(0.20f, 0.75f, 0.68f, 1.0f), X, Y, 6.0f, Height);
	DrawText(TicketBoothOpenPrompt, FLinearColor::White, X + 28.0f, Y + 17.0f, nullptr, 1.35f);
}

void AOddsWellSportsbookHUD::DrawTicketBoothUnavailableMenu()
{
	const float Width = FMath::Min(720.0f, Canvas->SizeX - 56.0f);
	const float Height = 330.0f;
	const float X = (Canvas->SizeX - Width) * 0.5f;
	const float Y = (Canvas->SizeY - Height) * 0.5f;
	const FLinearColor Navy(0.025f, 0.055f, 0.08f, 0.985f);
	const FLinearColor Muted(0.70f, 0.73f, 0.76f, 1.0f);
	const FLinearColor Gold(0.96f, 0.78f, 0.30f, 1.0f);

	DrawRect(FLinearColor(0.0f, 0.0f, 0.0f, 0.62f), 0.0f, 0.0f, Canvas->SizeX, Canvas->SizeY);
	DrawRect(Navy, X, Y, Width, Height);
	DrawRect(Gold, X, Y, Width, 5.0f);
	DrawText(TEXT("STADIUM TICKET BOOTH"), FLinearColor::White, X + 26.0f, Y + 24.0f, nullptr, 1.55f);
	DrawText(TEXT("MATCH WINNER UNAVAILABLE / LOCKED"), Gold, X + 26.0f, Y + 90.0f, nullptr, 1.30f);
	DrawText(TEXT("The canonical local-beta offer is missing, invalid, or locked at server tipoff."), Muted, X + 26.0f, Y + 139.0f, nullptr, 1.0f);
	DrawText(TEXT("No teams, prices, selections, or wager controls are shown."), Muted, X + 26.0f, Y + 176.0f, nullptr, 1.0f);
	DrawText(TEXT("E or ESC: CLOSE"), FLinearColor::White, X + 26.0f, Y + Height - 52.0f, nullptr, 0.90f);

	const float CloseWidth = 92.0f;
	const float CloseX = X + Width - CloseWidth - 18.0f;
	const float CloseY = Y + 18.0f;
	DrawRect(FLinearColor(0.16f, 0.19f, 0.22f, 1.0f), CloseX, CloseY, CloseWidth, 38.0f);
	DrawText(TEXT("X  CLOSE"), FLinearColor::White, CloseX + 13.0f, CloseY + 10.0f, nullptr, 0.90f);
	AddHitBox(FVector2D(CloseX, CloseY), FVector2D(CloseWidth, 38.0f), TEXT("TicketBoothClose"), true, 20);
}

void AOddsWellSportsbookHUD::DrawTicketBoothSettledLossReceipt(
	const FOddsWellCanonicalSettledLossReceipt& Receipt)
{
	const float Width = FMath::Min(720.0f, Canvas->SizeX - 56.0f);
	const float Height = 520.0f;
	const float X = (Canvas->SizeX - Width) * 0.5f;
	const float Y = (Canvas->SizeY - Height) * 0.5f;
	DrawRect(
		FLinearColor(0.0f, 0.0f, 0.0f, 0.62f),
		0.0f,
		0.0f,
		Canvas->SizeX,
		Canvas->SizeY);
	DrawRect(FLinearColor(0.025f, 0.055f, 0.08f, 0.985f), X, Y, Width, Height);
	DrawRect(FLinearColor(0.96f, 0.78f, 0.30f, 1.0f), X, Y, Width, 5.0f);
	TArray<FString> Lines;
	BuildCanonicalSettledLossReceiptText(Receipt).ParseIntoArrayLines(
		Lines,
		false);
	for (int32 Index = 0; Index < Lines.Num(); ++Index)
	{
		DrawText(
			Lines[Index],
			Index == 0
				? FLinearColor(0.96f, 0.78f, 0.30f, 1.0f)
				: FLinearColor::White,
			X + 42.0f,
			Y + 38.0f + Index * 48.0f,
			nullptr,
			Index == 0 ? 1.55f : 1.08f);
	}
}

void AOddsWellSportsbookHUD::DrawMarketCard(
	const FString& Title,
	const FString& Subtitle,
	const float X,
	const float Y,
	const float Width,
	const float Height,
	const bool bAvailable)
{
	const FLinearColor Card = bAvailable
		? FLinearColor(0.075f, 0.18f, 0.22f, 1.0f)
		: FLinearColor(0.085f, 0.10f, 0.13f, 1.0f);
	const FLinearColor Accent = bAvailable
		? FLinearColor(0.20f, 0.75f, 0.68f, 1.0f)
		: FLinearColor(0.42f, 0.46f, 0.50f, 1.0f);
	DrawRect(Card, X, Y, Width, Height);
	DrawRect(Accent, X, Y, 5.0f, Height);
	DrawText(Title, FLinearColor::White, X + 20.0f, Y + 16.0f, nullptr, 1.20f);
	DrawText(Subtitle, bAvailable ? FLinearColor(0.96f, 0.78f, 0.30f) : FLinearColor(0.70f, 0.73f, 0.76f), X + 20.0f, Y + 49.0f, nullptr, 1.05f);
	DrawText(
		bAvailable ? TEXT("SELECT FOR REVIEW") : TEXT("LOCKED - ODDS NOT PUBLISHED"),
		Accent,
		X + 20.0f,
		Y + Height - 30.0f,
		nullptr,
		0.85f);
}

void AOddsWellSportsbookHUD::DrawTicketBoothMenu(
	const AOddsWellPlaceholderCharacter& Character,
	const FOddsWellMatchWinnerOfferPreview& Offer)
{
	const float Margin = 28.0f;
	const float X = Margin;
	const float Y = Margin;
	const float Width = Canvas->SizeX - Margin * 2.0f;
	const float Height = Canvas->SizeY - Margin * 2.0f;
	const float HeaderHeight = 86.0f;
	const float TabHeight = 54.0f;
	const float ContentY = Y + HeaderHeight + TabHeight + 18.0f;
	const float ContentHeight = Height - HeaderHeight - TabHeight - 38.0f;
	const float SlipWidth = FMath::Clamp(Width * 0.29f, 300.0f, 390.0f);
	const float Gap = 18.0f;
	const float MarketWidth = Width - SlipWidth - Gap - 36.0f;
	const float MarketX = X + 18.0f;
	const float SlipX = MarketX + MarketWidth + Gap;
	const FLinearColor Navy(0.025f, 0.055f, 0.08f, 0.985f);
	const FLinearColor Panel(0.055f, 0.085f, 0.11f, 1.0f);
	const FLinearColor Teal(0.20f, 0.75f, 0.68f, 1.0f);
	const FLinearColor Gold(0.96f, 0.78f, 0.30f, 1.0f);
	const FLinearColor Muted(0.70f, 0.73f, 0.76f, 1.0f);

	DrawRect(FLinearColor(0.0f, 0.0f, 0.0f, 0.62f), 0.0f, 0.0f, Canvas->SizeX, Canvas->SizeY);
	DrawRect(Navy, X, Y, Width, Height);
	DrawRect(Teal, X, Y, Width, 5.0f);
	DrawText(TEXT("STADIUM TICKET BOOTH"), FLinearColor::White, X + 24.0f, Y + 20.0f, nullptr, 1.55f);
	DrawText(
		FString::Printf(TEXT("BASKETBALL  |  PRE-GAME  |  %s at %s  |  LOCAL BETA"), *Offer.AwayTeam, *Offer.HomeTeam),
		Muted,
		X + 24.0f,
		Y + 54.0f,
		nullptr,
		0.95f);

	const float CloseWidth = 92.0f;
	const float CloseX = X + Width - CloseWidth - 18.0f;
	const float CloseY = Y + 18.0f;
	DrawRect(FLinearColor(0.16f, 0.19f, 0.22f, 1.0f), CloseX, CloseY, CloseWidth, 38.0f);
	DrawText(TEXT("X  CLOSE"), FLinearColor::White, CloseX + 13.0f, CloseY + 10.0f, nullptr, 0.90f);
	AddHitBox(FVector2D(CloseX, CloseY), FVector2D(CloseWidth, 38.0f), TEXT("TicketBoothClose"), true, 20);

	const TArray<FString>& Labels = GetTicketBoothMarketLabels();
	const float TabY = Y + HeaderHeight;
	const float TabWidth = Width / Labels.Num();
	for (int32 Index = 0; Index < Labels.Num(); ++Index)
	{
		const float TabX = X + TabWidth * Index;
		const bool bActive = Index == Character.GetTicketBoothMarketPage();
		DrawRect(bActive ? FLinearColor(0.10f, 0.34f, 0.34f, 1.0f) : Panel, TabX, TabY, TabWidth - 2.0f, TabHeight);
		if (bActive)
		{
			DrawRect(Gold, TabX, TabY + TabHeight - 5.0f, TabWidth - 2.0f, 5.0f);
		}
		DrawText(
			bActive ? FString::Printf(TEXT("%s  ACTIVE"), *Labels[Index]) : Labels[Index],
			bActive ? FLinearColor::White : Muted,
			TabX + 15.0f,
			TabY + 18.0f,
			nullptr,
			0.90f);
		AddHitBox(
			FVector2D(TabX, TabY),
			FVector2D(TabWidth - 2.0f, TabHeight),
			FName(*FString::Printf(TEXT("TicketBoothTab%d"), Index)),
			true,
			10);
	}

	DrawRect(Panel, MarketX, ContentY, MarketWidth, ContentHeight);
	const float InnerX = MarketX + 20.0f;
	const float InnerWidth = MarketWidth - 40.0f;
	const int32 Page = Character.GetTicketBoothMarketPage();
	DrawText(Labels[Page], FLinearColor::White, InnerX, ContentY + 18.0f, nullptr, 1.35f);

	if (Page == 0 && Offer.Selections.Num() == 2)
	{
		DrawText(TEXT("MATCH WINNER  |  DECIMAL ODDS"), Muted, InnerX, ContentY + 53.0f, nullptr, 0.95f);
		const float CardY = ContentY + 88.0f;
		const float CardGap = 14.0f;
		const float CardWidth = (InnerWidth - CardGap) * 0.5f;
		for (int32 Index = 0; Index < Offer.Selections.Num(); ++Index)
		{
			const FOddsWellMatchWinnerSelectionPreview& Selection = Offer.Selections[Index];
			const float SelectionX =
				InnerX + Index * (CardWidth + CardGap);
			const FString Odds = FString::Printf(
				TEXT("%.4f DECIMAL"),
				static_cast<double>(Selection.DecimalOddsE4) / 10000.0);
			DrawMarketCard(
				Selection.Team,
				Odds,
				SelectionX,
				CardY,
				CardWidth,
				134.0f,
				true);
			if (Character.CanReviewTicketBoothBetSlip())
			{
				const bool bSelected =
					Character.GetTicketBoothReviewSelectionIndex() == Index;
				if (bSelected)
				{
					DrawRect(Gold, SelectionX, CardY, CardWidth, 5.0f);
					DrawText(
						TEXT("SELECTED"),
						Gold,
						SelectionX + CardWidth - 88.0f,
						CardY + 16.0f,
						nullptr,
						0.82f);
				}
				AddHitBox(
					FVector2D(SelectionX, CardY),
					FVector2D(CardWidth, 134.0f),
					Index == 0
						? TicketBoothHomeTeamHitBox
						: TicketBoothAwayTeamHitBox,
					true,
					15);
			}
		}
		DrawText(TEXT("Click a team or use , / . or D-pad left / right"), Muted, InnerX, CardY + 160.0f, nullptr, 0.95f);
		DrawText(
			FString::Printf(
				TEXT("%lld Odds Bucks returns %lld or %lld, based on your selection"),
				Offer.MinimumStake,
				Offer.Selections[0].MinimumStakeGrossReturn,
				Offer.Selections[1].MinimumStakeGrossReturn),
			FLinearColor::White,
			InnerX,
			CardY + 190.0f,
			nullptr,
			1.0f);
	}
	else if (Page == 1)
	{
		DrawText(TEXT("FUTURE SCORE-MARGIN MARKETS"), Muted, InnerX, ContentY + 53.0f, nullptr, 0.95f);
		const float CardWidth = (InnerWidth - 28.0f) / 3.0f;
		DrawMarketCard(TEXT("WIN BY 1-5"), TEXT("Either team"), InnerX, ContentY + 88.0f, CardWidth, 134.0f, false);
		DrawMarketCard(TEXT("WIN BY 6-10"), TEXT("Either team"), InnerX + CardWidth + 14.0f, ContentY + 88.0f, CardWidth, 134.0f, false);
		DrawMarketCard(TEXT("WIN BY 11+"), TEXT("Either team"), InnerX + (CardWidth + 14.0f) * 2.0f, ContentY + 88.0f, CardWidth, 134.0f, false);
	}
	else if (Page == 2)
	{
		DrawText(TEXT("FUTURE GAME OUTCOME MARKET"), Muted, InnerX, ContentY + 53.0f, nullptr, 0.95f);
		const float CardWidth = (InnerWidth - 14.0f) * 0.5f;
		DrawMarketCard(TEXT("OVERTIME - YES"), TEXT("Game reaches overtime"), InnerX, ContentY + 88.0f, CardWidth, 134.0f, false);
		DrawMarketCard(TEXT("OVERTIME - NO"), TEXT("Game ends in regulation"), InnerX + CardWidth + 14.0f, ContentY + 88.0f, CardWidth, 134.0f, false);
	}
	else
	{
		DrawText(TEXT("FUTURE ATHLETE MARKETS"), Muted, InnerX, ContentY + 53.0f, nullptr, 0.95f);
		const float CardWidth = (InnerWidth - 28.0f) / 3.0f;
		DrawMarketCard(TEXT("POINTS"), TEXT("Over / under"), InnerX, ContentY + 88.0f, CardWidth, 134.0f, false);
		DrawMarketCard(TEXT("REBOUNDS"), TEXT("Over / under"), InnerX + CardWidth + 14.0f, ContentY + 88.0f, CardWidth, 134.0f, false);
		DrawMarketCard(TEXT("PERSONAL FOULS"), TEXT("Over / under"), InnerX + (CardWidth + 14.0f) * 2.0f, ContentY + 88.0f, CardWidth, 134.0f, false);
	}

	DrawText(
		Page == 0
			? TEXT("Only validated Match Winner odds are published.")
			: TEXT("This category stays locked until its event and settlement proof passes."),
		Page == 0 ? Teal : Gold,
		InnerX,
		ContentY + ContentHeight - 46.0f,
		nullptr,
		0.95f);

	DrawRect(FLinearColor(0.96f, 0.94f, 0.87f, 1.0f), SlipX, ContentY, SlipWidth, ContentHeight);
	const FOddsWellCanonicalPendingMatchWinnerReceipt* Receipt =
		Character.GetTicketBoothCanonicalReceipt();
	if (Receipt)
	{
		DrawText(TEXT("BET ACCEPTED"), FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 20.0f, nullptr, 1.35f);
		DrawText(TEXT("PENDING TIPOFF"), FLinearColor(0.08f, 0.45f, 0.42f), SlipX + 20.0f, ContentY + 55.0f, nullptr, 0.92f);
		DrawRect(FLinearColor(0.84f, 0.82f, 0.76f, 1.0f), SlipX + 20.0f, ContentY + 92.0f, SlipWidth - 40.0f, 2.0f);
		DrawText(TEXT("SELECTION"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 116.0f, nullptr, 0.82f);
		DrawText(Receipt->SelectedTeam, FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 145.0f, nullptr, 1.05f);
		DrawText(TEXT("STAKE / POTENTIAL GROSS"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 194.0f, nullptr, 0.82f);
		DrawText(FString::Printf(TEXT("%lld Odds Bucks  /  %lld gross"), Receipt->Stake, Receipt->GrossReturn), FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 223.0f, nullptr, 1.05f);
		DrawText(TEXT("CURRENT BALANCE"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 272.0f, nullptr, 0.82f);
		DrawText(FString::Printf(TEXT("%lld Odds Bucks"), Receipt->CurrentBalance), FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 301.0f, nullptr, 1.0f);
		DrawText(TEXT("LOCKED AT GAME START"), FLinearColor(0.55f, 0.22f, 0.12f), SlipX + 20.0f, ContentY + ContentHeight - 116.0f, nullptr, 0.92f);
		DrawText(TEXT("Odds Bucks only. No real money."), FLinearColor(0.55f, 0.22f, 0.12f), SlipX + 20.0f, ContentY + ContentHeight - 85.0f, nullptr, 0.92f);
		DrawText(TEXT("LEFT / RIGHT: MARKET    E or ESC: CLOSE"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + ContentHeight - 43.0f, nullptr, 0.78f);
		return;
	}

	const bool bReviewAvailable = Character.CanReviewTicketBoothBetSlip();
	const int32 SelectionIndex =
		Character.GetTicketBoothReviewSelectionIndex();
	const FOddsWellMatchWinnerSelectionPreview* Selection =
		bReviewAvailable && Offer.Selections.IsValidIndex(SelectionIndex)
			? &Offer.Selections[SelectionIndex]
			: nullptr;
	const int64 Stake = Character.GetTicketBoothReviewStake();
	DrawText(TEXT("BET SLIP"), FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 20.0f, nullptr, 1.35f);
	DrawText(Selection ? TEXT("PRE-COMMIT REVIEW") : TEXT("CHOOSE A TEAM"), FLinearColor(0.08f, 0.45f, 0.42f), SlipX + 20.0f, ContentY + 55.0f, nullptr, 0.92f);
	DrawRect(FLinearColor(0.84f, 0.82f, 0.76f, 1.0f), SlipX + 20.0f, ContentY + 92.0f, SlipWidth - 40.0f, 2.0f);
	DrawText(TEXT("SELECTION / DECIMAL ODDS"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 112.0f, nullptr, 0.82f);
	DrawText(
		Selection
			? FString::Printf(TEXT("%s  |  %.4f"), *Selection->Team, static_cast<double>(Selection->DecimalOddsE4) / 10000.0)
			: TEXT("Select Harbor or Mesa"),
		FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 140.0f, nullptr, 0.94f);
	DrawText(TEXT("STAKE"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 184.0f, nullptr, 0.82f);
	const float StakeY = ContentY + 210.0f;
	DrawRect(FLinearColor(0.16f, 0.19f, 0.22f, 1.0f), SlipX + 20.0f, StakeY, 42.0f, 38.0f);
	DrawText(TEXT("-"), FLinearColor::White, SlipX + 35.0f, StakeY + 8.0f, nullptr, 1.10f);
	DrawText(FString::Printf(TEXT("%lld Odds Bucks"), Stake), FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 74.0f, StakeY + 9.0f, nullptr, 0.94f);
	DrawRect(FLinearColor(0.16f, 0.19f, 0.22f, 1.0f), SlipX + SlipWidth - 62.0f, StakeY, 42.0f, 38.0f);
	DrawText(TEXT("+"), FLinearColor::White, SlipX + SlipWidth - 48.0f, StakeY + 8.0f, nullptr, 1.10f);
	if (bReviewAvailable)
	{
		AddHitBox(FVector2D(SlipX + 20.0f, StakeY), FVector2D(42.0f, 38.0f), TicketBoothStakeDecreaseHitBox, true, 15);
		AddHitBox(FVector2D(SlipX + SlipWidth - 62.0f, StakeY), FVector2D(42.0f, 38.0f), TicketBoothStakeIncreaseHitBox, true, 15);
	}
	DrawText(TEXT("POTENTIAL GROSS RETURN"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 270.0f, nullptr, 0.82f);
	DrawText(
		Selection
			? FString::Printf(TEXT("%lld Odds Bucks"), Character.GetTicketBoothReviewGrossReturn())
			: TEXT("Select a team to calculate"),
		FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 298.0f, nullptr, 1.0f);
	DrawText(TEXT("CURRENT BALANCE"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + 342.0f, nullptr, 0.82f);
	DrawText(FString::Printf(TEXT("%lld Odds Bucks"), Character.GetTicketBoothCurrentBalance()), FLinearColor(0.025f, 0.055f, 0.08f), SlipX + 20.0f, ContentY + 370.0f, nullptr, 1.0f);
	const bool bPlacementAvailable =
		Character.CanPlaceTicketBoothCanonicalForty();
	const bool bArmed = Character.IsTicketBoothWagerArmed();
	const FString SelectedTeam = Selection ? Selection->Team : FString();
	const float ConfirmY = ContentY + ContentHeight - 180.0f;
	DrawRect(
		bPlacementAvailable
			? (bArmed ? FLinearColor(0.65f, 0.18f, 0.12f, 1.0f) : FLinearColor(0.08f, 0.45f, 0.42f, 1.0f))
			: FLinearColor(0.52f, 0.50f, 0.46f, 1.0f),
		SlipX + 20.0f,
		ConfirmY,
		SlipWidth - 40.0f,
		42.0f);
	DrawText(
		bPlacementAvailable
			? (bArmed
				? FString::Printf(TEXT("CONFIRM %s / 40"), *SelectedTeam)
				: FString::Printf(TEXT("ARM %s / 40"), *SelectedTeam))
			: TEXT("PLACEMENT UNAVAILABLE"),
		FLinearColor::White,
		SlipX + 34.0f,
		ConfirmY + 11.0f,
		nullptr,
		0.90f);
	if (bPlacementAvailable)
	{
		AddHitBox(
			FVector2D(SlipX + 20.0f, ConfirmY),
			FVector2D(SlipWidth - 40.0f, 42.0f),
			TicketBoothConfirmHitBox,
			true,
			15);
	}
	DrawText(
		bArmed
			? TEXT("ARMED - CONFIRM AGAIN TO PLACE")
			: (bPlacementAvailable
				? TEXT("FIRST CONFIRM ONLY ARMS - NO DEBIT")
				: TEXT("SELECT HARBOR OR MESA AT 40")),
		bArmed ? FLinearColor(0.65f, 0.18f, 0.12f) : FLinearColor(0.32f, 0.34f, 0.36f),
		SlipX + 20.0f,
		ConfirmY + 47.0f,
		nullptr,
		0.72f);
	DrawText(TEXT("LOCKS AT GAME START"), FLinearColor(0.55f, 0.22f, 0.12f), SlipX + 20.0f, ContentY + ContentHeight - 116.0f, nullptr, 0.88f);
	DrawText(bArmed ? TEXT("ARMED \u2014 WAGER NOT PLACED") : TEXT("WAGER NOT PLACED"), FLinearColor(0.55f, 0.22f, 0.12f), SlipX + 20.0f, ContentY + ContentHeight - 88.0f, nullptr, 0.86f);
	DrawText(TEXT(", / . OR D-PAD LEFT / RIGHT: TEAM"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + ContentHeight - 56.0f, nullptr, 0.72f);
	DrawText(TEXT("ENTER / GAMEPAD A / BUTTON: CONFIRM"), FLinearColor(0.32f, 0.34f, 0.36f), SlipX + 20.0f, ContentY + ContentHeight - 34.0f, nullptr, 0.72f);
}

void AOddsWellSportsbookHUD::NotifyHitBoxClick(const FName BoxName)
{
	Super::NotifyHitBoxClick(BoxName);
	AOddsWellPlaceholderCharacter* Character = GetOddsWellCharacter();
	if (!Character)
	{
		return;
	}
	if (BoxName == TEXT("TicketBoothClose"))
	{
		Character->CloseTicketBoothMenu();
		return;
	}
	if (BoxName == TicketBoothHomeTeamHitBox
		|| BoxName == TicketBoothAwayTeamHitBox)
	{
		Character->SelectTicketBoothReviewTeam(
			BoxName == TicketBoothHomeTeamHitBox ? 0 : 1);
		return;
	}
	if (BoxName == TicketBoothStakeDecreaseHitBox)
	{
		Character->DecreaseTicketBoothReviewStake();
		return;
	}
	if (BoxName == TicketBoothStakeIncreaseHitBox)
	{
		Character->IncreaseTicketBoothReviewStake();
		return;
	}
	if (BoxName == TicketBoothConfirmHitBox)
	{
		Character->ConfirmTicketBoothWager();
		return;
	}
	for (int32 Index = 0; Index < TicketBoothMarketPageCount; ++Index)
	{
		if (BoxName == FName(*FString::Printf(TEXT("TicketBoothTab%d"), Index)))
		{
			Character->SetTicketBoothMarketPage(Index);
			return;
		}
	}
}

AOddsWellLocomotionGameMode::AOddsWellLocomotionGameMode()
{
	PrimaryActorTick.bCanEverTick = true;
	DefaultPawnClass = AOddsWellPlaceholderCharacter::StaticClass();
	HUDClass = AOddsWellSportsbookHUD::StaticClass();
	bSharedCityQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityQa"));
	bSharedCityReconnectQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityReconnectQa"));
	bSharedCityCapacityQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityCapacityQa"));
	SharedCityQaTargetClients = GetSharedCityQaTargetClients();
}

void AOddsWellLocomotionGameMode::BeginPlay()
{
	Super::BeginPlay();
	FOddsWellCanonicalScheduledGameRecord CanonicalScheduledGame;
	FString CanonicalScheduleError;
	const EOddsWellCanonicalScheduledGameResult CanonicalScheduleResult =
		CreateOddsWellCanonicalLocalBetaScheduledGame(
			CanonicalScheduledGame,
			CanonicalScheduleError);
	if (CanonicalScheduleResult == EOddsWellCanonicalScheduledGameResult::Rejected)
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_SCHEDULE|result=FAIL|detail=%s"),
			*CanonicalScheduleError);
	}
	else
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_SCHEDULE|result=PASS|transition=%s|season=1|game=1|home=Harbor City Waves|away=Mesa Vista Sol|season_created_unix=%lld|tipoff_unix=%lld|offer_eligible_unix=%lld|offer_published=false|status=scheduled_unplayed|environment=local_beta|timing_authority=server|production_timing=false"),
			CanonicalScheduleResult == EOddsWellCanonicalScheduledGameResult::Created
				? TEXT("created")
				: TEXT("duplicate"),
			CanonicalScheduledGame.SeasonCreatedUnixSeconds,
			CanonicalScheduledGame.TipoffUnixSeconds,
			CanonicalScheduledGame.OfferEligibleUnixSeconds);
		FOddsWellCanonicalPregameCommitmentRecord PregameCommitment;
		FString PregameCommitmentError;
		const EOddsWellCanonicalPregameCommitmentResult PregameCommitmentResult =
			CreateOddsWellCanonicalPregameCommitment(
				PregameCommitment,
				PregameCommitmentError);
		if (PregameCommitmentResult == EOddsWellCanonicalPregameCommitmentResult::Rejected)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Error,
				TEXT("ODDSWELL_CANONICAL_PREGAME_COMMITMENT|result=FAIL|detail=%s"),
				*PregameCommitmentError);
		}
		else
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_CANONICAL_PREGAME_COMMITMENT|result=PASS|transition=%s|season=1|game=1|home=Harbor City Waves|away=Mesa Vista Sol|schedule_created_unix=%lld|tipoff_unix=%lld|snapshot=oddswell-public-pregame-v1|prediction=phase0d4-v1|input_class=public_elo_rotation|commitment_sha256=%s|standings=0-0,0-0|rest_days=7,7|availability=public|projected_minutes=public|offer=false|odds=false|ui=false|wager=false|simulation=false|result_state=false|environment=local_beta"),
				PregameCommitmentResult
						== EOddsWellCanonicalPregameCommitmentResult::Created
					? TEXT("created")
					: TEXT("duplicate"),
				PregameCommitment.ScheduleCreatedUnixSeconds,
				PregameCommitment.ScheduleTipoffUnixSeconds,
				*PregameCommitment.CommitmentSha256);
			FOddsWellCanonicalMatchWinnerOfferRecord CanonicalOffer;
			FString CanonicalOfferError;
			const EOddsWellCanonicalMatchWinnerOfferResult CanonicalOfferResult =
				CreateOddsWellCanonicalMatchWinnerOffer(
					CanonicalOffer,
					CanonicalOfferError);
			if (CanonicalOfferResult == EOddsWellCanonicalMatchWinnerOfferResult::Rejected)
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Error,
					TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_OFFER|result=FAIL|detail=%s"),
					*CanonicalOfferError);
			}
			else
			{
				UE_LOG(
					LogOddsWellLocomotion,
					Display,
					TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_OFFER|result=PASS|transition=%s|offer_id=%s|schema=oddswell-basketball-odds-offer-v1|offer_version=basketball-match-winner-odds-v1|market=match_winner|currency=odds_bucks|season=1|game=1|home=Harbor City Waves|away=Mesa Vista Sol|lock_unix=%lld|source_snapshot=oddswell-public-pregame-v1|source_prediction=phase0d4-v1|source_model=public_elo_rotation|source_commitment_sha256=898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f|probabilities_e8=57586693,42413307|decimal_odds_e4=17365,23577|stake=10-100|increment=10|edge_bps=0|payout=floor(stake*100000000/win_probability_e8)|upstream_mutation=false|ui=false|slip=false|request=false|debit=false|lock_transition=false|simulation=false|result=false|settlement=false|environment=local_beta"),
					CanonicalOfferResult
							== EOddsWellCanonicalMatchWinnerOfferResult::Created
						? TEXT("created")
						: TEXT("duplicate"),
					*CanonicalOffer.OfferId,
					CanonicalOffer.LockUnixSeconds);
			}
		}
	}
	bOddsBucksQaSlot = UseOddsWellOddsBucksQaSlot();
	bSportsbookWagerQa = FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQaVerify"));
	bSportsbookLockQaVerify = FParse::Param(FCommandLine::Get(), TEXT("SportsbookLockQaVerify"));
	bSportsbookLockQa = FParse::Param(FCommandLine::Get(), TEXT("SportsbookLockQa"))
		|| bSportsbookLockQaVerify;
	SportsbookLockQaStage = bSportsbookLockQaVerify ? 1 : 0;
	bSportsbookCancellationQaVerify = FParse::Param(FCommandLine::Get(), TEXT("SportsbookCancellationQaVerify"));
	bSportsbookCancellationQa = FParse::Param(FCommandLine::Get(), TEXT("SportsbookCancellationQa"))
		|| bSportsbookCancellationQaVerify;
	SportsbookCancellationQaStage = bSportsbookCancellationQaVerify ? 1 : 0;
	bSportsbookVoidDecisionQaVerify = FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidDecisionQaVerify"));
	bSportsbookVoidDecisionQa = FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidDecisionQa"))
		|| bSportsbookVoidDecisionQaVerify;
	bSportsbookVoidFinalizationQaVerify = FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidFinalizationQaVerify"));
	bSportsbookVoidFinalizationQa = FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidFinalizationQa"))
		|| bSportsbookVoidFinalizationQaVerify;
	const bool bCanonicalRequestQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerRequestQaVerify"));
	const bool bCanonicalRequestQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerRequestQa"))
		|| bCanonicalRequestQaVerify;
	const bool bCanonicalHarborFortyPlacementQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalHarborFortyPlacementQa"));
	const bool bCanonicalMesaFortyPlacementQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMesaFortyPlacementQa"));
	const bool bCanonicalAutomaticTipoffLockQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQa"));
	const bool bCanonicalPendingReceiptQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalPendingReceiptQa"));
	const bool bCanonicalLockQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLockQaVerify"));
	const bool bCanonicalLockQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLockQa"))
		|| bCanonicalLockQaVerify;
	const bool bCanonicalPostLockQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalPostLockQa"));
	const bool bCanonicalExecutionCommitmentQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalExecutionCommitmentQaVerify"));
	const bool bCanonicalExecutionCommitmentQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalExecutionCommitmentQa"))
		|| bCanonicalExecutionCommitmentQaVerify;
	const bool bCanonicalExecutionHandoffQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalExecutionHandoffQaVerify"));
	const bool bCanonicalExecutionHandoffQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalExecutionHandoffQa"))
		|| bCanonicalExecutionHandoffQaVerify;
	const bool bCanonicalResultLinkQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerResultLinkQaVerify"));
	const bool bCanonicalResultLinkQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerResultLinkQa"))
		|| bCanonicalResultLinkQaVerify;
	const bool bCanonicalLossDecisionQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLossDecisionQaVerify"));
	const bool bCanonicalLossDecisionQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLossDecisionQa"))
		|| bCanonicalLossDecisionQaVerify;
	const bool bCanonicalLossFinalizationQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLossFinalizationQaVerify"));
	const bool bCanonicalLossFinalizationQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLossFinalizationQa"))
		|| bCanonicalLossFinalizationQaVerify;
	const bool bCanonicalLossReconciliationQaVerify =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLossReconciliationQaVerify"));
	const bool bCanonicalLossReconciliationQa =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalMatchWinnerLossReconciliationQa"))
		|| bCanonicalLossReconciliationQaVerify;
	if (bCanonicalLossReconciliationQa)
	{
		const FString SourcePath = FPaths::Combine(
			FPaths::ProjectSavedDir(),
			TEXT("SaveGames/OddsWellOddsBucksQA.sav"));
		TArray<uint8> BeforeBytes;
		const FDateTime BeforeModified =
			IFileManager::Get().GetTimeStamp(*SourcePath);
		FString ProjectionPath;
		FString Error;
		bool bPassed = FFileHelper::LoadFileToArray(
			BeforeBytes,
			*SourcePath)
			&& WriteOddsWellCanonicalMatchWinnerLossReconciliation(
				true,
				ProjectionPath,
				Error);
		TArray<uint8> AfterBytes;
		FString Projection;
		const bool bSourceReloaded =
			FFileHelper::LoadFileToArray(AfterBytes, *SourcePath);
		const bool bSourceBytesStable =
			bSourceReloaded && BeforeBytes == AfterBytes;
		const bool bSourceMtimeStable = BeforeModified
			== IFileManager::Get().GetTimeStamp(*SourcePath);
		bPassed = bPassed
			&& bSourceBytesStable
			&& bSourceMtimeStable
			&& FFileHelper::LoadFileToString(
				Projection,
				*ProjectionPath);
		const bool bRetainedProjection = bPassed
			&& Projection.Contains(
				TEXT("\"offer_id\": \"1b5c696d7f9fd63a01e4f7d611d77834c4cccf23a97e811ac8d0f887c9183631\""))
			&& Projection.Contains(
				TEXT("\"result_command_id\": \"canonical:h26l:match_winner:result:e4b8b4e26126612e1173b4509c67666df44cfcf7082b51051e9de0097f45d0c6\""))
			&& Projection.Contains(
				TEXT("\"replay_seal_sha256\": \"efe7575962c88e9b8b4fcfcb6357c5307c6eeedd828b4b8f532c6e5eae985f62\""))
			&& Projection.Contains(TEXT("\"home_score\": 97"))
			&& Projection.Contains(TEXT("\"away_score\": 101"));
		const bool bCurrentProjection = bPassed
			&& Projection.Contains(
				TEXT("\"offer_id\": \"c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d\""))
			&& Projection.Contains(
				TEXT("\"result_command_id\": \"canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289\""))
			&& Projection.Contains(
				TEXT("\"replay_seal_sha256\": \"35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db\""))
			&& Projection.Contains(TEXT("\"home_score\": 79"))
			&& Projection.Contains(TEXT("\"away_score\": 113"));
		bPassed = bPassed
			&& (bRetainedProjection || bCurrentProjection)
			&& Projection.Contains(
				TEXT("\"schema\": \"oddswell-match-winner-reconciliation-v1\""))
			&& Projection.Contains(
				TEXT("\"selected_team\": \"Harbor City Waves\""))
			&& Projection.Contains(
				TEXT("\"selected_win_probability_e8\": 57586693"))
			&& Projection.Contains(
				TEXT("\"selected_decimal_odds_e4\": 17365"))
			&& Projection.Contains(
				TEXT("\"potential_gross_return\": 69"))
			&& Projection.Contains(
				TEXT("\"winner\": \"Mesa Vista Sol\""))
			&& Projection.Contains(TEXT("\"outcome\": \"lost\""))
			&& Projection.Contains(
				TEXT("\"decision_status\": \"decided_pending_apply\""))
			&& Projection.Contains(
				TEXT("\"finalization_status\": \"settled_lost\""))
			&& Projection.Contains(TEXT("\"gross_return_applied\": 0"))
			&& Projection.Contains(TEXT("\"ledger_entry_count\": 2"))
			&& Projection.Contains(TEXT("\"final_balance\": 60"))
			&& Projection.Contains(TEXT("\"net\": -40"));
		const FString OfferId = bCurrentProjection
			? TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d")
			: TEXT("1b5c696d7f9fd63a01e4f7d611d77834c4cccf23a97e811ac8d0f887c9183631");
		const FString ResultSha = bCurrentProjection
			? TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289")
			: TEXT("e4b8b4e26126612e1173b4509c67666df44cfcf7082b51051e9de0097f45d0c6");
		const FString FinalScore = bCurrentProjection ? TEXT("79-113") : TEXT("97-101");
		bool bCleanup = false;
		if (bPassed && bCanonicalLossReconciliationQaVerify)
		{
			bCleanup = ResetOddsWellQaOddsBucksAndVerify(Error);
			bPassed = bCleanup;
		}
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_LOSS_RECONCILIATION_QA|result=%s|schema=oddswell-match-winner-reconciliation-v1|offer_id=%s|result_sha=%s|selected_team=Harbor_City_Waves|probability_e8=57586693|decimal_odds_e4=17365|stake=40|potential_return=69|final_score=%s|winner=Mesa_Vista_Sol|outcome=lost|gross_return_due=0|gross_return_applied=0|decision_status=decided_pending_apply|finalization_status=settled_lost|ledger_entries=2|final_balance=60|net=-40|read_only=true|source_bytes_stable=%s|source_mtime_stable=%s|controls=false|mutation=false|payout=false|refund=false|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*OfferId,
			*ResultSha,
			*FinalScore,
			bSourceBytesStable ? TEXT("true") : TEXT("false"),
			bSourceMtimeStable ? TEXT("true") : TEXT("false"),
			bCleanup ? TEXT("true") : TEXT("false"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalLossFinalizationQa)
	{
		FOddsWellOddsBucksLedger BeforeLedger;
		int64 BeforeNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> BeforeRequests;
		TArray<FOddsWellMatchWinnerLockRecord> BeforeLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> BeforeResults;
		TArray<FOddsWellMatchWinnerSettlementDecisionRecord>
			BeforeDecisions;
		TArray<FOddsWellMatchWinnerLossFinalizationRecord>
			BeforeLossFinalizations;
		TArray<FOddsWellMatchWinnerWinFinalizationRecord>
			BeforeWinFinalizations;
		bool bBeforeFound = false;
		FString Error;
		bool bPassed =
			LoadOddsWellOddsBucksWagerFinalizationState(
				true,
				BeforeLedger,
				BeforeNextJobPayoutUnixSeconds,
				BeforeRequests,
				BeforeLocks,
				BeforeResults,
				BeforeDecisions,
				BeforeLossFinalizations,
				BeforeWinFinalizations,
				bBeforeFound,
				Error)
			&& bBeforeFound
			&& BeforeLedger.GetEntries().Num() == 2
			&& BeforeLedger.GetEntries()[0].Delta == 100
			&& BeforeLedger.GetEntries()[0].BalanceAfter == 100
			&& BeforeLedger.GetEntries()[1].Delta == -40
			&& BeforeLedger.GetEntries()[1].BalanceAfter == 60
			&& BeforeLedger.GetBalance() == 60
			&& BeforeRequests.Num() == 1
			&& BeforeRequests[0].OfferedTeam
				== TEXT("Harbor City Waves")
			&& BeforeRequests[0].Stake == 40
			&& BeforeLocks.Num() == 1
			&& BeforeResults.Num() == 1
			&& BeforeResults[0].Winner
				== TEXT("Mesa Vista Sol")
			&& BeforeDecisions.Num() == 1
			&& BeforeDecisions[0].SelectedTeam
				== TEXT("Harbor City Waves")
			&& BeforeDecisions[0].AuthoritativeWinner
				== TEXT("Mesa Vista Sol")
			&& BeforeDecisions[0].Stake == 40
			&& BeforeDecisions[0].Outcome
				== FName(TEXT("lost"))
			&& BeforeDecisions[0].GrossReturnDue == 0
			&& BeforeDecisions[0].Status
				== FName(TEXT("decided_pending_apply"))
			&& BeforeLossFinalizations.Num()
				== (bCanonicalLossFinalizationQaVerify ? 1 : 0)
			&& BeforeWinFinalizations.IsEmpty();
		TArray<uint8> BeforeBytes;
		bPassed = bPassed
			&& UGameplayStatics::SaveGameToMemory(
				UGameplayStatics::LoadGameFromSlot(
					TEXT("OddsWellOddsBucksQA"),
					0),
				BeforeBytes);
		FOddsWellMatchWinnerLossFinalizationRecord Finalization;
		const EOddsWellMatchWinnerLossFinalizationResult Result =
			bPassed
				? FinalizeOddsWellCanonicalMatchWinnerLoss(
					Finalization,
					Error)
				: EOddsWellMatchWinnerLossFinalizationResult::Rejected;
		const FString ExpectedFinalizationId =
			BeforeDecisions.Num() == 1
				? TEXT("canonical:h26n:match_winner:finalization:")
					+ BeforeDecisions[0].DecisionCommandId.RightChop(
						FString(
							TEXT(
								"canonical:h26m:match_winner:decision:"))
							.Len())
				: FString();
		bPassed = bPassed
			&& Result
				== (bCanonicalLossFinalizationQaVerify
					? EOddsWellMatchWinnerLossFinalizationResult::Duplicate
					: EOddsWellMatchWinnerLossFinalizationResult::Finalized)
			&& Finalization.FinalizationCommandId
				== ExpectedFinalizationId
			&& Finalization.DecisionCommandId
				== BeforeDecisions[0].DecisionCommandId
			&& Finalization.RequestCommandId
				== BeforeRequests[0].RequestCommandId
			&& Finalization.LockCommandId
				== BeforeLocks[0].LockCommandId
			&& Finalization.ResultCommandId
				== BeforeResults[0].ResultCommandId
			&& Finalization.FinalizationSchema
				== TEXT(
					"oddswell-match-winner-loss-finalization-v1")
			&& Finalization.FinalizationVersion
				== TEXT(
					"match-winner-loss-finalization-v1")
			&& Finalization.SelectedTeam
				== TEXT("Harbor City Waves")
			&& Finalization.AuthoritativeWinner
				== TEXT("Mesa Vista Sol")
			&& Finalization.Stake == 40
			&& Finalization.Outcome == FName(TEXT("lost"))
			&& Finalization.GrossReturnApplied == 0
			&& Finalization.Status
				== FName(TEXT("settled_lost"))
			&& Finalization.ObservedFinalBalance == 60
			&& Finalization.ObservedLedgerEntryCount == 2;

		FOddsWellOddsBucksLedger AfterLedger;
		int64 AfterNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> AfterRequests;
		TArray<FOddsWellMatchWinnerLockRecord> AfterLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> AfterResults;
		TArray<FOddsWellMatchWinnerSettlementDecisionRecord>
			AfterDecisions;
		TArray<FOddsWellMatchWinnerLossFinalizationRecord>
			AfterLossFinalizations;
		TArray<FOddsWellMatchWinnerWinFinalizationRecord>
			AfterWinFinalizations;
		bool bAfterFound = false;
		bPassed = bPassed
			&& LoadOddsWellOddsBucksWagerFinalizationState(
				true,
				AfterLedger,
				AfterNextJobPayoutUnixSeconds,
				AfterRequests,
				AfterLocks,
				AfterResults,
				AfterDecisions,
				AfterLossFinalizations,
				AfterWinFinalizations,
				bAfterFound,
				Error)
			&& bAfterFound
			&& AfterLedger.GetEntries().Num() == 2
			&& AfterLedger.GetEntries()[0].CommandId
				== BeforeLedger.GetEntries()[0].CommandId
			&& AfterLedger.GetEntries()[0].Delta == 100
			&& AfterLedger.GetEntries()[1].CommandId
				== BeforeLedger.GetEntries()[1].CommandId
			&& AfterLedger.GetEntries()[1].Delta == -40
			&& AfterLedger.GetBalance() == 60
			&& AfterNextJobPayoutUnixSeconds
				== BeforeNextJobPayoutUnixSeconds
			&& AfterRequests.Num() == 1
			&& AfterLocks.Num() == 1
			&& AfterResults.Num() == 1
			&& AfterDecisions.Num() == 1
			&& AfterDecisions[0].DecisionCommandId
				== BeforeDecisions[0].DecisionCommandId
			&& AfterDecisions[0].GrossReturnDue == 0
			&& AfterDecisions[0].Status
				== FName(TEXT("decided_pending_apply"))
			&& AfterLossFinalizations.Num() == 1
			&& AfterLossFinalizations[0].FinalizationCommandId
				== Finalization.FinalizationCommandId
			&& AfterWinFinalizations.IsEmpty();
		const UOddsWellOddsBucksSaveGame* ExactState =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					TEXT("OddsWellOddsBucksQA"),
					0));
		bPassed = bPassed
			&& ExactState
			&& ExactState->SchemaVersion == 12
			&& ExactState->MatchWinnerCanceledGames.IsEmpty()
			&& ExactState->MatchWinnerVoidDecisions.IsEmpty()
			&& ExactState->MatchWinnerVoidFinalizations.IsEmpty();
		bool bDuplicateByteStable =
			!bCanonicalLossFinalizationQaVerify;
		if (bPassed && bCanonicalLossFinalizationQaVerify)
		{
			TArray<uint8> AfterBytes;
			bDuplicateByteStable =
				UGameplayStatics::SaveGameToMemory(
					UGameplayStatics::LoadGameFromSlot(
						TEXT("OddsWellOddsBucksQA"),
						0),
					AfterBytes)
				&& BeforeBytes == AfterBytes;
			bPassed = bPassed && bDuplicateByteStable;
		}
		bool bCleanup = false;
		if (bPassed && bCanonicalLossFinalizationQaVerify)
		{
			bCleanup =
				ResetOddsWellQaOddsBucksAndVerify(Error);
			bPassed = bCleanup;
		}
		const FString ObservedTransition =
			Result
				== EOddsWellMatchWinnerLossFinalizationResult::Finalized
				? TEXT("finalized")
				: Result
					== EOddsWellMatchWinnerLossFinalizationResult::Duplicate
					? TEXT("duplicate")
					: TEXT("rejected");
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_LOSS_FINALIZATION_QA|result=%s|transition=%s|cold_process_restore=%s|finalization_command_id=%s|decision_command_id=%s|request_command_id=%s|lock_command_id=%s|result_command_id=%s|finalization_schema=%s|finalization_version=%s|season=1|game=1|selected_team=%s|authoritative_winner=%s|stake=%lld|outcome=%s|gross_return_due=0|gross_return_applied=%lld|decision_status=decided_pending_apply|status=%s|schema_version=12|ledger_entries=%d|balance=%lld|requests=%d|locks=%d|result_links=%d|decisions=%d|loss_finalizations=%d|win_finalizations=%d|cancellations=%d|voids=%d|duplicate_byte_stable=%s|caller_input=false|new_ledger_entry=false|credit=false|payout=false|refund=false|history=false|ui=false|admin=false|correction=false|replay=false|stats=false|simulation=false|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*ObservedTransition,
			bCanonicalLossFinalizationQaVerify
				? TEXT("true")
				: TEXT("false"),
			*Finalization.FinalizationCommandId,
			*Finalization.DecisionCommandId,
			*Finalization.RequestCommandId,
			*Finalization.LockCommandId,
			*Finalization.ResultCommandId,
			Finalization.FinalizationSchema.IsEmpty()
				? TEXT("none")
				: *Finalization.FinalizationSchema,
			Finalization.FinalizationVersion.IsEmpty()
				? TEXT("none")
				: *Finalization.FinalizationVersion,
			Finalization.SelectedTeam.IsEmpty()
				? TEXT("none")
				: *Finalization.SelectedTeam,
			Finalization.AuthoritativeWinner.IsEmpty()
				? TEXT("none")
				: *Finalization.AuthoritativeWinner,
			Finalization.Stake,
			Finalization.Outcome.IsNone()
				? TEXT("none")
				: *Finalization.Outcome.ToString(),
			Finalization.GrossReturnApplied,
			Finalization.Status.IsNone()
				? TEXT("none")
				: *Finalization.Status.ToString(),
			bAfterFound ? AfterLedger.GetEntries().Num() : 0,
			bAfterFound ? AfterLedger.GetBalance() : 0,
			bAfterFound ? AfterRequests.Num() : 0,
			bAfterFound ? AfterLocks.Num() : 0,
			bAfterFound ? AfterResults.Num() : 0,
			bAfterFound ? AfterDecisions.Num() : 0,
			bAfterFound ? AfterLossFinalizations.Num() : 0,
			bAfterFound ? AfterWinFinalizations.Num() : 0,
			ExactState
				? ExactState->MatchWinnerCanceledGames.Num()
				: 0,
			ExactState
				? ExactState->MatchWinnerVoidDecisions.Num()
				: 0,
			bDuplicateByteStable
				? TEXT("true")
				: TEXT("false"),
			bCleanup ? TEXT("true") : TEXT("false"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("%s"),
				*Evidence);
		}
		else
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Error,
				TEXT("%s"),
				*Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalLossDecisionQa)
	{
		FOddsWellOddsBucksLedger BeforeLedger;
		int64 BeforeNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> BeforeRequests;
		TArray<FOddsWellMatchWinnerLockRecord> BeforeLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> BeforeResults;
		TArray<FOddsWellMatchWinnerSettlementDecisionRecord>
			BeforeDecisions;
		bool bBeforeFound = false;
		FString Error;
		bool bPassed =
			LoadOddsWellOddsBucksWagerDecisionState(
				true,
				BeforeLedger,
				BeforeNextJobPayoutUnixSeconds,
				BeforeRequests,
				BeforeLocks,
				BeforeResults,
				BeforeDecisions,
				bBeforeFound,
				Error)
			&& bBeforeFound
			&& BeforeLedger.GetEntries().Num() == 2
			&& BeforeLedger.GetEntries()[0].Delta == 100
			&& BeforeLedger.GetEntries()[1].Delta == -40
			&& BeforeLedger.GetBalance() == 60
			&& BeforeRequests.Num() == 1
			&& BeforeRequests[0].OfferedTeam
				== TEXT("Harbor City Waves")
			&& BeforeRequests[0].Stake == 40
			&& BeforeLocks.Num() == 1
			&& BeforeResults.Num() == 1
			&& BeforeResults[0].Winner
				== TEXT("Mesa Vista Sol")
			&& BeforeDecisions.Num()
				== (bCanonicalLossDecisionQaVerify ? 1 : 0);
		TArray<uint8> BeforeBytes;
		bPassed = bPassed
			&& UGameplayStatics::SaveGameToMemory(
				UGameplayStatics::LoadGameFromSlot(
					TEXT("OddsWellOddsBucksQA"),
					0),
				BeforeBytes);
		FOddsWellMatchWinnerSettlementDecisionRecord Decision;
		const EOddsWellMatchWinnerSettlementDecisionResult Result =
			bPassed
				? DecideOddsWellCanonicalMatchWinnerLossDecision(
					Decision,
					Error)
				: EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
		const FString ExpectedDecisionId =
			BeforeResults.Num() == 1
				? TEXT("canonical:h26m:match_winner:decision:")
					+ BeforeResults[0].ResultCommandId.RightChop(
						FString(
							TEXT(
								"canonical:h26l:match_winner:result:"))
							.Len())
				: FString();
		bPassed = bPassed
			&& Result
				== (bCanonicalLossDecisionQaVerify
					? EOddsWellMatchWinnerSettlementDecisionResult::Duplicate
					: EOddsWellMatchWinnerSettlementDecisionResult::Decided)
			&& Decision.DecisionCommandId == ExpectedDecisionId
			&& Decision.RequestCommandId
				== BeforeRequests[0].RequestCommandId
			&& Decision.LockCommandId
				== BeforeLocks[0].LockCommandId
			&& Decision.ResultCommandId
				== BeforeResults[0].ResultCommandId
			&& Decision.DecisionSchema
				== TEXT(
					"oddswell-match-winner-settlement-decision-v1")
			&& Decision.DecisionVersion
				== TEXT(
					"match-winner-settlement-decision-v1")
			&& Decision.OfferId == BeforeRequests[0].OfferId
			&& Decision.OfferVersion
				== BeforeRequests[0].OfferVersion
			&& Decision.SelectedTeam
				== TEXT("Harbor City Waves")
			&& Decision.AuthoritativeWinner
				== TEXT("Mesa Vista Sol")
			&& Decision.Stake == 40
			&& Decision.Outcome == FName(TEXT("lost"))
			&& Decision.GrossReturnDue == 0
			&& Decision.SelectedWinProbabilityE8 == 0
			&& Decision.PayoutFormula.IsEmpty()
			&& Decision.Status
				== FName(TEXT("decided_pending_apply"));

		FOddsWellOddsBucksLedger AfterLedger;
		int64 AfterNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> AfterRequests;
		TArray<FOddsWellMatchWinnerLockRecord> AfterLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> AfterResults;
		TArray<FOddsWellMatchWinnerSettlementDecisionRecord>
			AfterDecisions;
		bool bAfterFound = false;
		bPassed = bPassed
			&& LoadOddsWellOddsBucksWagerDecisionState(
				true,
				AfterLedger,
				AfterNextJobPayoutUnixSeconds,
				AfterRequests,
				AfterLocks,
				AfterResults,
				AfterDecisions,
				bAfterFound,
				Error)
			&& bAfterFound
			&& AfterLedger.GetEntries().Num() == 2
			&& AfterLedger.GetEntries()[0].CommandId
				== BeforeLedger.GetEntries()[0].CommandId
			&& AfterLedger.GetEntries()[0].Delta == 100
			&& AfterLedger.GetEntries()[0].BalanceAfter == 100
			&& AfterLedger.GetEntries()[1].CommandId
				== BeforeLedger.GetEntries()[1].CommandId
			&& AfterLedger.GetEntries()[1].Delta == -40
			&& AfterLedger.GetEntries()[1].BalanceAfter == 60
			&& AfterLedger.GetBalance() == 60
			&& AfterNextJobPayoutUnixSeconds
				== BeforeNextJobPayoutUnixSeconds
			&& AfterRequests.Num() == 1
			&& AfterLocks.Num() == 1
			&& AfterResults.Num() == 1
			&& AfterDecisions.Num() == 1
			&& AfterDecisions[0].DecisionCommandId
				== Decision.DecisionCommandId;
		const UOddsWellOddsBucksSaveGame* ExactState =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					TEXT("OddsWellOddsBucksQA"),
					0));
		bPassed = bPassed
			&& ExactState
			&& ExactState->SchemaVersion == 12
			&& ExactState->MatchWinnerLossFinalizations.IsEmpty()
			&& ExactState->MatchWinnerWinFinalizations.IsEmpty()
			&& ExactState->MatchWinnerCanceledGames.IsEmpty()
			&& ExactState->MatchWinnerVoidDecisions.IsEmpty()
			&& ExactState->MatchWinnerVoidFinalizations.IsEmpty();
		bool bDuplicateByteStable =
			!bCanonicalLossDecisionQaVerify;
		if (bPassed && bCanonicalLossDecisionQaVerify)
		{
			TArray<uint8> AfterBytes;
			bDuplicateByteStable =
				UGameplayStatics::SaveGameToMemory(
					UGameplayStatics::LoadGameFromSlot(
						TEXT("OddsWellOddsBucksQA"),
						0),
					AfterBytes)
				&& BeforeBytes == AfterBytes;
			bPassed = bPassed && bDuplicateByteStable;
		}
		bool bCleanup = false;
		if (bPassed && bCanonicalLossDecisionQaVerify)
		{
			bCleanup =
				ResetOddsWellQaOddsBucksAndVerify(Error);
			bPassed = bCleanup;
		}
		const FOddsWellOddsBucksLedger& ObservedLedger =
			bAfterFound ? AfterLedger : BeforeLedger;
		const int32 ObservedResultLinks =
			bAfterFound ? AfterResults.Num() : BeforeResults.Num();
		const int32 ObservedDecisions =
			bAfterFound
				? AfterDecisions.Num()
				: BeforeDecisions.Num();
		const FString ObservedTransition =
			Result
				== EOddsWellMatchWinnerSettlementDecisionResult::Decided
				? TEXT("decided")
				: Result
					== EOddsWellMatchWinnerSettlementDecisionResult::Duplicate
					? TEXT("duplicate")
					: TEXT("rejected");
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_LOSS_DECISION_QA|result=%s|transition=%s|cold_process_restore=%s|decision_command_id=%s|request_command_id=%s|lock_command_id=%s|result_command_id=%s|decision_schema=%s|decision_version=%s|season=1|game=1|selected_team=%s|authoritative_winner=%s|stake=%lld|outcome=%s|gross_return_due=%lld|status=%s|schema_version=12|ledger_entries=%d|balance=%lld|result_links=%d|decisions=%d|loss_finalizations=%d|win_finalizations=%d|cancellations=%d|voids=%d|duplicate_byte_stable=%s|caller_input=false|finalization=false|application=false|history=false|ui=false|admin=false|replay=false|stats=false|simulation=false|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*ObservedTransition,
			bCanonicalLossDecisionQaVerify
				? TEXT("true")
				: TEXT("false"),
			*Decision.DecisionCommandId,
			*Decision.RequestCommandId,
			*Decision.LockCommandId,
			*Decision.ResultCommandId,
			Decision.DecisionSchema.IsEmpty()
				? TEXT("none")
				: *Decision.DecisionSchema,
			Decision.DecisionVersion.IsEmpty()
				? TEXT("none")
				: *Decision.DecisionVersion,
			Decision.SelectedTeam.IsEmpty()
				? TEXT("none")
				: *Decision.SelectedTeam,
			Decision.AuthoritativeWinner.IsEmpty()
				? TEXT("none")
				: *Decision.AuthoritativeWinner,
			Decision.Stake,
			Decision.Outcome.IsNone()
				? TEXT("none")
				: *Decision.Outcome.ToString(),
			Decision.GrossReturnDue,
			Decision.Status.IsNone()
				? TEXT("none")
				: *Decision.Status.ToString(),
			ObservedLedger.GetEntries().Num(),
			ObservedLedger.GetBalance(),
			ObservedResultLinks,
			ObservedDecisions,
			ExactState
				? ExactState->MatchWinnerLossFinalizations.Num()
				: 0,
			ExactState
				? ExactState->MatchWinnerWinFinalizations.Num()
				: 0,
			ExactState
				? ExactState->MatchWinnerCanceledGames.Num()
				: 0,
			ExactState
				? ExactState->MatchWinnerVoidDecisions.Num()
				: 0,
			bDuplicateByteStable
				? TEXT("true")
				: TEXT("false"),
			bCleanup ? TEXT("true") : TEXT("false"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("%s"),
				*Evidence);
		}
		else
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Error,
				TEXT("%s"),
				*Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalResultLinkQa)
	{
		FOddsWellOddsBucksLedger BeforeLedger;
		int64 BeforeNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> BeforeRequests;
		TArray<FOddsWellMatchWinnerLockRecord> BeforeLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> BeforeResults;
		bool bBeforeFound = false;
		FString Error;
		bool bPassed =
			LoadOddsWellOddsBucksWagerEvidence(
				true,
				BeforeLedger,
				BeforeNextJobPayoutUnixSeconds,
				BeforeRequests,
				BeforeLocks,
				BeforeResults,
				bBeforeFound,
				Error)
			&& bBeforeFound
			&& BeforeLedger.GetEntries().Num() == 2
			&& BeforeLedger.GetBalance() == 60
			&& BeforeRequests.Num() == 1
			&& BeforeLocks.Num() == 1
			&& BeforeResults.Num()
				== (bCanonicalResultLinkQaVerify ? 1 : 0);
		TArray<uint8> BeforeBytes;
		bPassed = bPassed
			&& UGameplayStatics::SaveGameToMemory(
				UGameplayStatics::LoadGameFromSlot(
					TEXT("OddsWellOddsBucksQA"),
					0),
				BeforeBytes);
		FOddsWellMatchWinnerResultLinkRecord Linked;
		const EOddsWellMatchWinnerResultLinkResult Result =
			bPassed
				? LinkOddsWellCanonicalMatchWinnerResult(
					Linked,
					Error)
				: EOddsWellMatchWinnerResultLinkResult::Rejected;
		bPassed = bPassed
			&& Result
				== (bCanonicalResultLinkQaVerify
					? EOddsWellMatchWinnerResultLinkResult::Duplicate
					: EOddsWellMatchWinnerResultLinkResult::Linked);
		FOddsWellOddsBucksLedger AfterLedger;
		int64 AfterNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> AfterRequests;
		TArray<FOddsWellMatchWinnerLockRecord> AfterLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> AfterResults;
		bool bAfterFound = false;
		bPassed = bPassed
			&& LoadOddsWellOddsBucksWagerEvidence(
				true,
				AfterLedger,
				AfterNextJobPayoutUnixSeconds,
				AfterRequests,
				AfterLocks,
				AfterResults,
				bAfterFound,
				Error)
			&& bAfterFound
			&& AfterLedger.GetEntries().Num() == 2
			&& AfterLedger.GetEntries()[1].Delta == -40
			&& AfterLedger.GetBalance() == 60
			&& AfterRequests.Num() == 1
			&& AfterLocks.Num() == 1
			&& AfterResults.Num() == 1
			&& AfterResults[0].ResultCommandId
				== Linked.ResultCommandId
			&& AfterResults[0].RequestCommandId
				== BeforeRequests[0].RequestCommandId
			&& AfterResults[0].LockCommandId
				== BeforeLocks[0].LockCommandId
			&& AfterResults[0].ResultSchema
				== TEXT(
					"oddswell-private-canonical-game-result-v1")
			&& AfterResults[0].ResultVersion
				== TEXT(
					"oddswell-private-game-result-recorder-v1")
			&& AfterResults[0].SeasonNumber == 1
			&& AfterResults[0].GameNumber == 1
			&& AfterResults[0].HomeTeam
				== TEXT("Harbor City Waves")
			&& AfterResults[0].AwayTeam
				== TEXT("Mesa Vista Sol")
			&& AfterResults[0].HomeScore >= 0
			&& AfterResults[0].AwayScore >= 0
			&& AfterResults[0].HomeScore
				!= AfterResults[0].AwayScore
			&& AfterResults[0].Winner
				== (AfterResults[0].HomeScore
						> AfterResults[0].AwayScore
					? AfterResults[0].HomeTeam
					: AfterResults[0].AwayTeam)
			&& AfterResults[0].ReplaySealSha256.Len() == 64
			&& AfterNextJobPayoutUnixSeconds
				== BeforeNextJobPayoutUnixSeconds;
		const UOddsWellOddsBucksSaveGame* ExactState =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					TEXT("OddsWellOddsBucksQA"),
					0));
		bPassed = bPassed
			&& ExactState
			&& ExactState->SchemaVersion == 12
			&& ExactState->MatchWinnerSettlementDecisions.IsEmpty()
			&& ExactState->MatchWinnerLossFinalizations.IsEmpty()
			&& ExactState->MatchWinnerWinFinalizations.IsEmpty()
			&& ExactState->MatchWinnerCanceledGames.IsEmpty()
			&& ExactState->MatchWinnerVoidDecisions.IsEmpty()
			&& ExactState->MatchWinnerVoidFinalizations.IsEmpty();
		bool bDuplicateByteStable =
			!bCanonicalResultLinkQaVerify;
		if (bPassed && bCanonicalResultLinkQaVerify)
		{
			TArray<uint8> AfterBytes;
			bDuplicateByteStable =
				UGameplayStatics::SaveGameToMemory(
					UGameplayStatics::LoadGameFromSlot(
						TEXT("OddsWellOddsBucksQA"),
						0),
					AfterBytes)
				&& BeforeBytes == AfterBytes;
			bPassed = bPassed && bDuplicateByteStable;
		}
		bool bCleanup = false;
		if (bPassed && bCanonicalResultLinkQaVerify)
		{
			bCleanup =
				ResetOddsWellQaOddsBucksAndVerify(Error);
			bPassed = bCleanup;
		}
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_RESULT_LINK_QA|result=%s|transition=%s|cold_process_restore=%s|schema=oddswell-private-canonical-game-result-v1|recorder_version=oddswell-private-game-result-recorder-v1|season=1|game=1|home=%s|away=%s|home_score=%d|away_score=%d|winner=%s|replay_sha256=%s|result_command_id=%s|request_link=true|lock_link=true|schema_version=12|ledger_entries=2|stake_delta=-40|balance=60|result_links=1|decisions=0|finalizations=0|cancellations=0|refunds=0|payouts=0|duplicate_byte_stable=%s|archive_fallback=false|caller_input=false|simulation=false|settlement=false|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			bCanonicalResultLinkQaVerify
				? TEXT("duplicate")
				: TEXT("linked"),
			bCanonicalResultLinkQaVerify
				? TEXT("true")
				: TEXT("false"),
			*Linked.HomeTeam,
			*Linked.AwayTeam,
			Linked.HomeScore,
			Linked.AwayScore,
			*Linked.Winner,
			*Linked.ReplaySealSha256,
			*Linked.ResultCommandId,
			bDuplicateByteStable
				? TEXT("true")
				: TEXT("false"),
			bCleanup ? TEXT("true") : TEXT("false"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("%s"),
				*Evidence);
		}
		else
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Error,
				TEXT("%s"),
				*Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalExecutionHandoffQa)
	{
		FString HandoffPath;
		FString HandoffSha256;
		FString Error;
		const EOddsWellCanonicalGameExecutionHandoffResult Result =
			WriteOddsWellCanonicalGameExecutionHandoff(
				HandoffPath,
				HandoffSha256,
				Error);
		FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
		const bool bPassed =
			Result == (
				bCanonicalExecutionHandoffQaVerify
					? EOddsWellCanonicalGameExecutionHandoffResult::Duplicate
					: EOddsWellCanonicalGameExecutionHandoffResult::Created)
			&& LoadOddsWellCanonicalActiveGameExecutionCommitment(
				Commitment,
				Error)
			&& Commitment.Status == TEXT("committed_for_execution")
			&& HandoffSha256.Len() == 64;
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_EXECUTION_HANDOFF_QA|result=%s|transition=%s|cold_process_restore=%s|schema=oddswell-canonical-active-game-execution-commitment-v1|record_version=1|status=committed_for_execution|commitment_sha256=%s|execution_input_sha256=%s|handoff_sha256=%s|private=true|caller_seed=false|caller_input=false|caller_version=false|caller_team=false|caller_wager=false|caller_time=false|caller_output=false|caller_path=false|runtime_python=false|service=false|port=false|simulation=false|result=false|seal=false|settlement=false|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			bCanonicalExecutionHandoffQaVerify
				? TEXT("duplicate")
				: TEXT("created"),
			bCanonicalExecutionHandoffQaVerify
				? TEXT("true")
				: TEXT("false"),
			*Commitment.CommitmentSha256,
			*Commitment.ExecutionInputSha256,
			*HandoffSha256,
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalExecutionCommitmentQa)
	{
		FOddsWellOddsBucksLedger BeforeLedger;
		int64 BeforeNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> BeforeRequests;
		TArray<FOddsWellMatchWinnerLockRecord> BeforeLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> BeforeResults;
		bool bBeforeFound = false;
		FString Error;
		bool bPassed =
			LoadOddsWellOddsBucksWagerEvidence(
				true,
				BeforeLedger,
				BeforeNextJobPayoutUnixSeconds,
				BeforeRequests,
				BeforeLocks,
				BeforeResults,
				bBeforeFound,
				Error)
			&& bBeforeFound
			&& BeforeLedger.GetEntries().Num() == 2
			&& BeforeLedger.GetBalance() == 60
			&& BeforeRequests.Num() == 1
			&& BeforeLocks.Num() == 1
			&& BeforeResults.IsEmpty();
		FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
		const EOddsWellCanonicalActiveGameExecutionCommitmentResult Result =
			bPassed
				? CreateOddsWellCanonicalActiveGameExecutionCommitment(
					Commitment,
					Error)
				: EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
		bPassed = bPassed
			&& Result == (
				bCanonicalExecutionCommitmentQaVerify
					? EOddsWellCanonicalActiveGameExecutionCommitmentResult::Duplicate
					: EOddsWellCanonicalActiveGameExecutionCommitmentResult::Created)
			&& Commitment.Schema
				== TEXT("oddswell-canonical-active-game-execution-commitment-v1")
			&& Commitment.RecordVersion == 1
			&& Commitment.SeasonNumber == 1
			&& Commitment.GameNumber == 1
			&& Commitment.Status == TEXT("committed_for_execution")
			&& Commitment.Environment == TEXT("local_beta")
			&& Commitment.SeedDerivationVersion
				== TEXT("oddswell-canonical-active-game-seed-v1")
			&& Commitment.SeedMaterialSha256.Len() == 64
			&& Commitment.ExecutionInputSha256.Len() == 64
			&& Commitment.CommitmentSha256.Len() == 64;
		FOddsWellOddsBucksLedger AfterLedger;
		int64 AfterNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> AfterRequests;
		TArray<FOddsWellMatchWinnerLockRecord> AfterLocks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> AfterResults;
		bool bAfterFound = false;
		bPassed = bPassed
			&& LoadOddsWellOddsBucksWagerEvidence(
				true,
				AfterLedger,
				AfterNextJobPayoutUnixSeconds,
				AfterRequests,
				AfterLocks,
				AfterResults,
				bAfterFound,
				Error)
			&& bAfterFound
			&& AfterLedger.GetEntries().Num()
				== BeforeLedger.GetEntries().Num()
			&& AfterLedger.GetBalance() == BeforeLedger.GetBalance()
			&& AfterRequests.Num() == BeforeRequests.Num()
			&& AfterLocks.Num() == BeforeLocks.Num()
			&& AfterResults.IsEmpty()
			&& AfterNextJobPayoutUnixSeconds
				== BeforeNextJobPayoutUnixSeconds;
		bool bMissingLockRejected = false;
		bool bCommitmentImmutable = false;
		bool bCleanup = !bCanonicalExecutionCommitmentQaVerify;
		if (bPassed && bCanonicalExecutionCommitmentQaVerify)
		{
			bCleanup = ResetOddsWellQaOddsBucksAndVerify(Error);
			FOddsWellCanonicalActiveGameExecutionCommitmentRecord RejectedRecord;
			const EOddsWellCanonicalActiveGameExecutionCommitmentResult
				MissingLockResult =
					bCleanup
						? CreateOddsWellCanonicalActiveGameExecutionCommitment(
							RejectedRecord,
							Error)
						: EOddsWellCanonicalActiveGameExecutionCommitmentResult::Created;
			bMissingLockRejected =
				bCleanup
				&& MissingLockResult
					== EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
			FOddsWellCanonicalActiveGameExecutionCommitmentRecord
				RestoredCommitment;
			bCommitmentImmutable =
				bMissingLockRejected
				&& LoadOddsWellCanonicalActiveGameExecutionCommitment(
					RestoredCommitment,
					Error)
				&& RestoredCommitment.SeedMaterialSha256
					== Commitment.SeedMaterialSha256
				&& RestoredCommitment.ExecutionInputSha256
					== Commitment.ExecutionInputSha256
				&& RestoredCommitment.CommitmentSha256
					== Commitment.CommitmentSha256
				&& RestoredCommitment.Status == Commitment.Status;
			bPassed = bPassed
				&& bMissingLockRejected
				&& bCommitmentImmutable;
			if (bPassed)
			{
				Error.Reset();
			}
		}
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_EXECUTION_COMMITMENT_QA|result=%s|transition=%s|cold_process_restore=%s|schema=oddswell-canonical-active-game-execution-commitment-v1|record_version=1|season=1|game=1|status=committed_for_execution|seed_derivation=sha256_h26a_h26b_only|execution_input_sha256=%s|commitment_sha256=%s|private_seed=true|private_input=true|public_offer_mutation=false|booth_mutation=false|league_export_mutation=false|reconciliation_mutation=false|ledger_entries=2|requests=1|locks=1|results=0|balance=60|simulation=false|result_state=false|settlement=false|missing_lock_rejected=%s|commitment_immutable=%s|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			bCanonicalExecutionCommitmentQaVerify
				? TEXT("duplicate")
				: TEXT("created"),
			bCanonicalExecutionCommitmentQaVerify
				? TEXT("true")
				: TEXT("false"),
			*Commitment.ExecutionInputSha256,
			*Commitment.CommitmentSha256,
			bCanonicalExecutionCommitmentQaVerify
				? (bMissingLockRejected ? TEXT("true") : TEXT("false"))
				: TEXT("not_run"),
			bCanonicalExecutionCommitmentQaVerify
				? (bCommitmentImmutable ? TEXT("true") : TEXT("false"))
				: TEXT("not_run"),
			bCleanup ? TEXT("true") : TEXT("false"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalLockQa)
	{
		FOddsWellMatchWinnerLockRecord Lock;
		FString Error;
		const EOddsWellMatchWinnerLockResult Result =
			LockOddsWellCanonicalMatchWinnerRequestAtGameStart(
				Lock,
				Error);
		FOddsWellOddsBucksLedger PersistedLedger;
		int64 PersistedNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> Requests;
		TArray<FOddsWellMatchWinnerLockRecord> Locks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
		bool bFound = false;
		bool bPassed =
			Result == (
				bCanonicalLockQaVerify
					? EOddsWellMatchWinnerLockResult::Duplicate
					: EOddsWellMatchWinnerLockResult::Locked)
			&& LoadOddsWellOddsBucksWagerEvidence(
				true,
				PersistedLedger,
				PersistedNextJobPayoutUnixSeconds,
				Requests,
				Locks,
				Results,
				bFound,
				Error)
			&& bFound
			&& PersistedLedger.GetEntries().Num() == 2
			&& PersistedLedger.GetBalance() == 60
			&& Requests.Num() == 1
			&& Locks.Num() == 1
			&& Results.IsEmpty()
			&& Requests[0].OfferedTeam == TEXT("Harbor City Waves")
			&& Requests[0].SelectedWinProbabilityE8 == 57586693
			&& Requests[0].SelectedDecimalOddsE4 == 17365
			&& Requests[0].Stake == 40
			&& Requests[0].GrossReturn == 69
			&& Requests[0].Status == FName(TEXT("accepted_pending_lock"))
			&& Locks[0].RequestCommandId == Requests[0].RequestCommandId
			&& Locks[0].Decision == FName(TEXT("locked"));
		bool bRejectionStable = true;
		if (bPassed && bCanonicalLockQaVerify)
		{
			FOddsWellMatchWinnerLockRecord Rejected;
			FString RejectionError;
			bRejectionStable =
				LockOddsWellMatchWinnerRequest(
					Requests[0].RequestCommandId,
					TEXT("canonical:h26g:conflicting-lock"),
					Requests[0].SeasonNumber,
					Requests[0].GameNumber,
					Requests[0].LockUnixSeconds,
					true,
					Rejected,
					RejectionError)
					== EOddsWellMatchWinnerLockResult::Rejected;
			FOddsWellOddsBucksLedger AfterLedger;
			int64 AfterNextJobPayoutUnixSeconds = 0;
			TArray<FOddsWellMatchWinnerRequestRecord> AfterRequests;
			TArray<FOddsWellMatchWinnerLockRecord> AfterLocks;
			TArray<FOddsWellMatchWinnerResultLinkRecord> AfterResults;
			bRejectionStable = bRejectionStable
				&& LoadOddsWellOddsBucksWagerEvidence(
					true,
					AfterLedger,
					AfterNextJobPayoutUnixSeconds,
					AfterRequests,
					AfterLocks,
					AfterResults,
					bFound,
					Error)
				&& AfterLedger.GetEntries().Num() == 2
				&& AfterLedger.GetBalance() == 60
				&& AfterRequests.Num() == 1
				&& AfterLocks.Num() == 1
				&& AfterResults.IsEmpty()
				&& AfterNextJobPayoutUnixSeconds
					== PersistedNextJobPayoutUnixSeconds;
			bPassed = bPassed && bRejectionStable;
		}
		bool bCleanup = true;
		if (bCanonicalLockQaVerify)
		{
			bCleanup = ResetOddsWellQaOddsBucksAndVerify(Error);
			bPassed = bPassed && bCleanup;
		}
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_LOCK_QA|result=%s|transition=%s|cold_process_restore=%s|season=1|game=1|selected_team=Harbor_City_Waves|probability_e8=57586693|odds_e4=17365|stake=40|gross_return=69|entries=2|requests=1|locks=1|balance=60|request_status=accepted_pending_lock|lock_decision=locked|authority=server|clock=exact_h26a_tipoff|caller_identity=false|caller_time=false|schema=12|separate_immutable_record=true|result=false|settlement=false|upstream_mutation=false|rejection_zero_mutation=%s|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			bCanonicalLockQaVerify ? TEXT("duplicate") : TEXT("locked"),
			bCanonicalLockQaVerify ? TEXT("true") : TEXT("false"),
			bCanonicalLockQaVerify
				? (bRejectionStable ? TEXT("true") : TEXT("false"))
				: TEXT("deferred_to_cold_verify"),
			bCanonicalLockQaVerify
				? (bCleanup ? TEXT("true") : TEXT("false"))
				: TEXT("deferred"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bCanonicalPostLockQa)
	{
		int64 PersistedNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> Requests;
		TArray<FOddsWellMatchWinnerLockRecord> Locks;
		TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
		FString Error;
		const bool bPassed =
			LoadOddsWellOddsBucksWagerEvidence(
				true,
				OddsBucksLedger,
				PersistedNextJobPayoutUnixSeconds,
				Requests,
				Locks,
				Results,
				bOddsBucksLoadedFromDisk,
				Error)
			&& bOddsBucksLoadedFromDisk
			&& OddsBucksLedger.GetEntries().Num() == 2
			&& OddsBucksLedger.GetBalance() == 60
			&& Requests.Num() == 1
			&& Locks.Num() == 1
			&& Results.IsEmpty();
		MatchWinnerRequestCount = Requests.Num();
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_POST_LOCK_MODE|result=%s|cold_process_restore=true|read_only=true|entries=%d|requests=%d|locks=%d|balance=%lld|write=false|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			OddsBucksLedger.GetEntries().Num(),
			Requests.Num(),
			Locks.Num(),
			OddsBucksLedger.GetBalance(),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		return;
	}
	if (bCanonicalPendingReceiptQa)
	{
		FOddsWellCanonicalPendingMatchWinnerReceipt Receipt;
		FString Error;
		const bool bPassed =
			LoadOddsWellCanonicalPendingMatchWinnerReceipt(
				Receipt,
				Error)
				== EOddsWellCanonicalPendingReceiptResult::Ready;
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_PENDING_RECEIPT_MODE|result=%s|cold_process_restore=true|read_only=true|request_api=false|migration=false|write=false|partial=false|selected_team=%s|stake=%lld|gross_return=%lld|balance=%lld|status=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*Receipt.SelectedTeam,
			Receipt.Stake,
			Receipt.GrossReturn,
			Receipt.CurrentBalance,
			*Receipt.Status.ToString(),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		return;
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("SportsbookReceiptQa")))
	{
		FOddsWellPendingQaMatchWinnerReceipt Receipt;
		FString Error;
		if (!LoadOddsWellPendingQaMatchWinnerReceipt(Receipt, Error))
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_ODDS_BUCKS_RECEIPT_MODE|result=FAIL|read_only=true|detail=%s"), *Error);
			return;
		}
		bOddsBucksLoadedFromDisk = true;
		MatchWinnerRequestCount = 1;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_ODDS_BUCKS_RECEIPT_MODE|result=PASS|cold_process_restore=true|read_only=true|request_api=false|reconciliation_write=false|request_id=%s|ledger_sequence=%lld|ledger_delta=%lld|balance=%lld"),
			*Receipt.RequestId,
			Receipt.LedgerSequence,
			Receipt.LedgerDelta,
			Receipt.CurrentBalance);
		return;
	}
	const bool bFreshJobQa = FParse::Param(FCommandLine::Get(), TEXT("JobQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQa"))
		|| (bCanonicalRequestQa && !bCanonicalRequestQaVerify)
		|| bCanonicalHarborFortyPlacementQa
		|| bCanonicalMesaFortyPlacementQa
		|| bCanonicalAutomaticTipoffLockQa;
	const bool bJobRecoveryQa = FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQa"));
	const bool bJobRecoveryQaVerify = FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQaVerify"));
	if (bSportsbookVoidFinalizationQa || bSportsbookVoidDecisionQa)
	{
		OddsBucksQaNowUnixSeconds = GetOddsWellUpcomingQaMatchWinnerCancellationUnixSeconds();
	}
	else if (bSportsbookCancellationQa)
	{
		OddsBucksQaNowUnixSeconds = GetOddsWellUpcomingQaMatchWinnerCancellationUnixSeconds()
			- (bSportsbookCancellationQaVerify ? 0 : 1);
	}
	else if (bSportsbookLockQa)
	{
		OddsBucksQaNowUnixSeconds = GetOddsWellUpcomingQaMatchWinnerLockUnixSeconds()
			- (bSportsbookLockQaVerify ? 0 : 1);
	}
	else if (bJobRecoveryQa || bJobRecoveryQaVerify || bSportsbookWagerQa)
	{
		OddsBucksQaNowUnixSeconds = bSportsbookWagerQa
			? GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds()
			: JobRecoveryQaStartUnixSeconds;
	}
	FString Error;
	if (bFreshJobQa && !ResetOddsWellQaOddsBucksAndVerify(Error))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_ODDS_BUCKS_LEDGER|result=FAIL|reason=qa_slot_reset_failed|detail=%s"), *Error);
		return;
	}
	TArray<FOddsWellMatchWinnerRequestRecord> MatchWinnerRequests;
	if (!LoadOddsWellOddsBucksState(bOddsBucksQaSlot, OddsBucksLedger, NextJobPayoutUnixSeconds, MatchWinnerRequests, bOddsBucksLoadedFromDisk, Error))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_ODDS_BUCKS_LEDGER|result=FAIL|reason=load_failed|detail=%s|payouts_enabled=false"), *Error);
		return;
	}
	MatchWinnerRequestCount = MatchWinnerRequests.Num();
	if (bJobRecoveryQaVerify && bOddsBucksLoadedFromDisk)
	{
		OddsBucksQaNowUnixSeconds = FMath::Max<int64>(1, NextJobPayoutUnixSeconds - 1);
	}
	bOddsBucksReady = true;
	ResumeCanonicalMatchWinnerResultLink();
	if (!bOddsBucksReady)
	{
		return;
	}
	PublishOddsBucksReconciliation();
	ScheduleCanonicalMatchWinnerTipoffLock();
	if (FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQa"))
		|| (bCanonicalRequestQa && !bCanonicalRequestQaVerify)
		|| bCanonicalHarborFortyPlacementQa
		|| bCanonicalMesaFortyPlacementQa
		|| bCanonicalAutomaticTipoffLockQa)
	{
		bool bCredited = false;
		int64 Balance = 0;
		int64 RetryAfterSeconds = 0;
		FString CommandId;
		if (!TryCreditPlaceholderJob(bCredited, Balance, RetryAfterSeconds, CommandId, Error)
			|| !bCredited
			|| Balance != GetOddsWellFirstJobPayout())
		{
			bOddsBucksReady = false;
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_WAGER|result=FAIL|reason=job_seed_failed|detail=%s"), *Error);
			return;
		}
	}
	if (bCanonicalRequestQa)
	{
		FOddsWellCanonicalMatchWinnerOfferRecord Offer;
		FOddsWellMatchWinnerRequestRecord Request;
		int64 Balance = 0;
		EOddsWellMatchWinnerRequestResult Result =
			EOddsWellMatchWinnerRequestResult::Rejected;
		bool bPassed =
			LoadOddsWellCanonicalMatchWinnerOffer(Offer, Error);
		if (bPassed)
		{
			Result = AcceptOddsWellCanonicalMatchWinnerRequest(
				Offer.OfferId,
				TEXT("Harbor City Waves"),
				40,
				Request,
				Balance,
				Error);
			bPassed =
				Result == (
					bCanonicalRequestQaVerify
						? EOddsWellMatchWinnerRequestResult::Duplicate
						: EOddsWellMatchWinnerRequestResult::Accepted);
		}
		FOddsWellOddsBucksLedger PersistedLedger;
		int64 PersistedNextJobPayoutUnixSeconds = 0;
		TArray<FOddsWellMatchWinnerRequestRecord> PersistedRequests;
		bool bPersistedFound = false;
		bPassed = bPassed
			&& LoadOddsWellOddsBucksState(
				true,
				PersistedLedger,
				PersistedNextJobPayoutUnixSeconds,
				PersistedRequests,
				bPersistedFound,
				Error)
			&& bPersistedFound
			&& PersistedLedger.GetEntries().Num() == 2
			&& PersistedLedger.GetBalance() == 60
			&& PersistedRequests.Num() == 1
			&& Request.EvidenceVersion == 1
			&& Request.OfferId == Offer.OfferId
			&& Request.OfferedTeam == TEXT("Harbor City Waves")
			&& Request.SelectedWinProbabilityE8 == 57586693
			&& Request.SelectedDecimalOddsE4 == 17365
			&& Request.Stake == 40
			&& Request.GrossReturn == 69
			&& Request.Status == FName(TEXT("accepted_pending_lock"));

		const int32 BeforeEntries = PersistedLedger.GetEntries().Num();
		const int32 BeforeRequests = PersistedRequests.Num();
		const int64 BeforeBalance = PersistedLedger.GetBalance();
		FOddsWellMatchWinnerRequestRecord Rejected;
		int64 RejectedBalance = 0;
		FString RejectionError;
		const bool bRejectionsPassed =
			AcceptOddsWellCanonicalMatchWinnerRequest(
				TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
				TEXT("Harbor City Waves"),
				40,
				Rejected,
				RejectedBalance,
				RejectionError)
				== EOddsWellMatchWinnerRequestResult::Rejected
			&& AcceptOddsWellCanonicalMatchWinnerRequest(
				Offer.OfferId,
				TEXT("Not Offered"),
				40,
				Rejected,
				RejectedBalance,
				RejectionError)
				== EOddsWellMatchWinnerRequestResult::Rejected
			&& AcceptOddsWellCanonicalMatchWinnerRequest(
				Offer.OfferId,
				TEXT("Harbor City Waves"),
				15,
				Rejected,
				RejectedBalance,
				RejectionError)
				== EOddsWellMatchWinnerRequestResult::Rejected;
		bPassed = bPassed
			&& bRejectionsPassed
			&& LoadOddsWellOddsBucksState(
				true,
				PersistedLedger,
				PersistedNextJobPayoutUnixSeconds,
				PersistedRequests,
				bPersistedFound,
				Error)
			&& PersistedLedger.GetEntries().Num() == BeforeEntries
			&& PersistedLedger.GetBalance() == BeforeBalance
			&& PersistedRequests.Num() == BeforeRequests;
		bool bCleanup = true;
		if (bCanonicalRequestQaVerify)
		{
			bCleanup = ResetOddsWellQaOddsBucksAndVerify(Error);
			bPassed = bPassed && bCleanup;
		}
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_CANONICAL_MATCH_WINNER_REQUEST_QA|result=%s|transition=%s|cold_process_restore=%s|offer_id=%s|request_id=%s|evidence_version=%d|season=1|game=1|selected_team=Harbor City Waves|selected_probability_e8=%lld|selected_decimal_odds_e4=%lld|stake=%lld|gross_return=%lld|accepted_unix=%lld|lock_unix=%lld|ledger_sequence=2|ledger_delta=-40|entries=%d|requests=%d|balance=%lld|status=accepted_pending_lock|server_time=true|caller_time=false|caller_price=false|normal_ui=false|automatic_normal_path=false|exact_retry=%s|rejection_audit=bad_offer,bad_team,bad_stake|zero_mutation=%s|atomic_failure=native_focused|upstream_mutation=false|archive_mutation=false|qa_offer_identity=false|cleanup=%s|detail=%s"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			bCanonicalRequestQaVerify ? TEXT("duplicate") : TEXT("accepted"),
			bCanonicalRequestQaVerify ? TEXT("true") : TEXT("false"),
			*Offer.OfferId,
			*Request.RequestCommandId,
			Request.EvidenceVersion,
			Request.SelectedWinProbabilityE8,
			Request.SelectedDecimalOddsE4,
			Request.Stake,
			Request.GrossReturn,
			Request.AcceptedUnixSeconds,
			Request.LockUnixSeconds,
			BeforeEntries,
			BeforeRequests,
			BeforeBalance,
			bCanonicalRequestQaVerify ? TEXT("duplicate") : TEXT("deferred_to_cold_process"),
			bRejectionsPassed ? TEXT("true") : TEXT("false"),
			bCanonicalRequestQaVerify
				? (bCleanup ? TEXT("true") : TEXT("false"))
				: TEXT("deferred"),
			Error.IsEmpty() ? TEXT("none") : *Error);
		if (bPassed)
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("%s"),
				*Evidence);
		}
		else
		{
			UE_LOG(
				LogOddsWellLocomotion,
				Error,
				TEXT("%s"),
				*Evidence);
		}
		FPlatformMisc::RequestExit(false);
		return;
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_ODDS_BUCKS_LEDGER|result=PASS|schema=oddswell-odds-bucks-ledger-v2|authority=server|currency=odds_bucks|source=%s|entries=%d|balance=%lld|starting_balance=0|job_payout=100|payout_interval_seconds=%lld|next_job_payout_unix=%lld|accumulation=true|allowance=false|append_only=true|idempotent=true|persistent_local_profile=true|client_commands=false|real_money=false|wagering=%s"),
		bOddsBucksLoadedFromDisk ? TEXT("disk") : TEXT("empty"),
		OddsBucksLedger.GetEntries().Num(),
		OddsBucksLedger.GetBalance(),
		GetOddsWellJobPayoutIntervalSeconds(),
		NextJobPayoutUnixSeconds,
		bSportsbookWagerQa ? TEXT("qa_only") : TEXT("false"));
}

void AOddsWellLocomotionGameMode::PublishOddsBucksReconciliation()
{
	FString Path;
	FString Error;
	if (!WriteOddsWellOddsBucksReconciliation(OddsBucksLedger, NextJobPayoutUnixSeconds, GetOddsBucksNowUnixSeconds(), bOddsBucksQaSlot, Path, Error))
	{
		UE_LOG(LogOddsWellLocomotion, Warning, TEXT("ODDSWELL_ODDS_BUCKS_RECONCILIATION|result=STALE|read_only=true|detail=%s"), *Error);
		return;
	}
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_ODDS_BUCKS_RECONCILIATION|result=PASS|read_only=true|qa=%s|entries=%d|balance=%lld|next_job_payout_unix=%lld|path=%s|backend=false|account=false"), bOddsBucksQaSlot ? TEXT("true") : TEXT("false"), OddsBucksLedger.GetEntries().Num(), OddsBucksLedger.GetBalance(), NextJobPayoutUnixSeconds, *Path);
}

int64 AOddsWellLocomotionGameMode::GetOddsBucksNowUnixSeconds() const
{
	return OddsBucksQaNowUnixSeconds > 0 ? OddsBucksQaNowUnixSeconds : FDateTime::UtcNow().ToUnixTimestamp();
}

bool AOddsWellLocomotionGameMode::AdvanceOddsBucksQaClock(const int64 Seconds)
{
	if (!bOddsBucksQaSlot || OddsBucksQaNowUnixSeconds <= 0 || Seconds < 0
		|| OddsBucksQaNowUnixSeconds > TNumericLimits<int64>::Max() - Seconds)
	{
		return false;
	}
	OddsBucksQaNowUnixSeconds += Seconds;
	return true;
}

bool AOddsWellLocomotionGameMode::TryCreditPlaceholderJob(bool& bOutCredited, int64& OutBalance, int64& OutRetryAfterSeconds, FString& OutCommandId, FString& OutError)
{
	bOutCredited = false;
	OutBalance = OddsBucksLedger.GetBalance();
	OutRetryAfterSeconds = 0;
	OutCommandId.Reset();
	if (!bOddsBucksReady || bSportsbookLockQa || bSportsbookCancellationQa || bSportsbookVoidDecisionQa || bSportsbookVoidFinalizationQa)
	{
		OutError = bSportsbookLockQa || bSportsbookCancellationQa || bSportsbookVoidDecisionQa || bSportsbookVoidFinalizationQa
			? TEXT("Job payouts are disabled during the isolated game-state transition.")
			: TEXT("The authoritative Odds Bucks ledger is not ready.");
		return false;
	}
	const int64 NowUnixSeconds = GetOddsBucksNowUnixSeconds();
	if (OddsBucksLedger.HasCommand(GetOddsWellFirstJobCommandId()))
	{
		if (NextJobPayoutUnixSeconds <= 0)
		{
			OutError = TEXT("The job payout schedule is missing.");
			return false;
		}
		if (NowUnixSeconds < NextJobPayoutUnixSeconds)
		{
			OutRetryAfterSeconds = NextJobPayoutUnixSeconds - NowUnixSeconds;
			OutError.Reset();
			return true;
		}
		OutCommandId = FString::Printf(TEXT("job:placeholder_shift:scheduled_payout:%lld"), NextJobPayoutUnixSeconds);
	}
	else
	{
		OutCommandId = GetOddsWellFirstJobCommandId();
	}
	FOddsWellOddsBucksLedger Candidate = OddsBucksLedger;
	const EOddsWellOddsBucksAppendResult Result = Candidate.Append(OutCommandId, GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason());
	if (Result != EOddsWellOddsBucksAppendResult::Applied)
	{
		OutError = TEXT("The scheduled job payout command was rejected.");
		return false;
	}
	if (NowUnixSeconds > TNumericLimits<int64>::Max() - GetOddsWellJobPayoutIntervalSeconds())
	{
		OutError = TEXT("The job payout schedule exceeds the supported clock range.");
		return false;
	}
	const int64 CandidateNextJobPayout = NowUnixSeconds + GetOddsWellJobPayoutIntervalSeconds();
	if (!SaveOddsWellOddsBucksLedger(Candidate, CandidateNextJobPayout, bOddsBucksQaSlot, OutError))
	{
		return false;
	}
	OddsBucksLedger = MoveTemp(Candidate);
	NextJobPayoutUnixSeconds = CandidateNextJobPayout;
	PublishOddsBucksReconciliation();
	bOutCredited = true;
	OutBalance = OddsBucksLedger.GetBalance();
	return true;
}

EOddsWellMatchWinnerRequestResult AOddsWellLocomotionGameMode::AcceptSportsbookQaWager(
	const FString& OfferedTeam,
	const int64 Stake,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	if (!bOddsBucksReady || !bOddsBucksQaSlot || !bSportsbookWagerQa || GetNetMode() != NM_Standalone)
	{
		OutError = TEXT("The isolated machine-local Sportsbook QA authority is unavailable.");
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	FOddsWellMatchWinnerOffer Offer;
	if (!BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, OutError))
	{
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	const EOddsWellMatchWinnerRequestResult Result = AcceptOddsWellUpcomingQaMatchWinnerRequest(
		Offer,
		GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
		OfferedTeam,
		Stake,
		GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
		OutRecord,
		OutBalance,
		OutError);
	if (Result == EOddsWellMatchWinnerRequestResult::Accepted || Result == EOddsWellMatchWinnerRequestResult::Duplicate)
	{
		TArray<FOddsWellMatchWinnerRequestRecord> Requests;
		bool bFound = false;
		if (!LoadOddsWellOddsBucksState(true, OddsBucksLedger, NextJobPayoutUnixSeconds, Requests, bFound, OutError) || !bFound)
		{
			OutError = FString::Printf(TEXT("The request is persisted, but the local ledger view could not reload: %s"), *OutError);
			return Result;
		}
		MatchWinnerRequestCount = Requests.Num();
		OutBalance = OddsBucksLedger.GetBalance();
		PublishOddsBucksReconciliation();
	}
	return Result;
}

EOddsWellMatchWinnerRequestResult AOddsWellLocomotionGameMode::AcceptCanonicalFortyWager(
	const bool bMesaSelected,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	if (!bOddsBucksReady)
	{
		OutError = TEXT("The Odds Bucks authority is unavailable.");
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	const EOddsWellMatchWinnerRequestResult Result =
		bMesaSelected
			? AcceptOddsWellCanonicalMesaFortyRequest(
				OutRecord,
				OutBalance,
				OutError)
			: AcceptOddsWellCanonicalHarborFortyRequest(
				OutRecord,
				OutBalance,
				OutError);
	if (Result == EOddsWellMatchWinnerRequestResult::Accepted
		|| Result == EOddsWellMatchWinnerRequestResult::Duplicate)
	{
		TArray<FOddsWellMatchWinnerRequestRecord> Requests;
		bool bFound = false;
		if (!LoadOddsWellOddsBucksState(
				bOddsBucksQaSlot,
				OddsBucksLedger,
				NextJobPayoutUnixSeconds,
				Requests,
				bFound,
				OutError)
			|| !bFound)
		{
			OutError = FString::Printf(
				TEXT("The request is durable, but the ledger view could not reload: %s"),
				*OutError);
			return Result;
		}
		MatchWinnerRequestCount = Requests.Num();
		OutBalance = OddsBucksLedger.GetBalance();
		PublishOddsBucksReconciliation();
		ScheduleCanonicalMatchWinnerTipoffLock();
	}
	return Result;
}

void AOddsWellLocomotionGameMode::ResumeCanonicalMatchWinnerResultLink()
{
	if (bOddsBucksQaSlot)
	{
		return;
	}
	TArray<FString> PrivateResultFiles;
	IFileManager::Get().FindFiles(
		PrivateResultFiles,
		*FPaths::Combine(
			FPaths::ProjectSavedDir(),
			TEXT("PrivateExecution"),
			TEXT("Results"),
			TEXT("*.json")),
		true,
		false);
	if (!ShouldAttemptCanonicalMatchWinnerResultLink(
			PrivateResultFiles.Num()))
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_RESULT_LINK|result=NOOP|phase=H26AE|reason=private_result_missing|booth=locked|mutation=false|polling=false|timer=false|watcher=false|process=false|h26m_to_h26p=false"));
		return;
	}

	FOddsWellMatchWinnerResultLinkRecord LinkedResult;
	FString Error;
	const EOddsWellMatchWinnerResultLinkResult Transition =
		LinkOddsWellCanonicalMatchWinnerResult(
			LinkedResult,
			Error);
	if (Transition == EOddsWellMatchWinnerResultLinkResult::Rejected)
	{
		if (CanResumeCanonicalLossDecisionAfterResultLinkRejection(
				Error))
		{
			ResumeCanonicalMatchWinnerDecision(true);
			return;
		}
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_RESULT_LINK|result=REJECTED|phase=H26AE|reason=link_rejected|booth=locked|mutation=false|polling=false|timer=false|watcher=false|process=false|h26m_to_h26p=false|detail=%s"),
			*Error);
		return;
	}

	FOddsWellOddsBucksLedger PersistedLedger;
	int64 PersistedNextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> PersistedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> PersistedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> PersistedResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> PersistedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> PersistedLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> PersistedWinFinalizations;
	bool bPersistedFound = false;
	const bool bDurable =
		LoadOddsWellOddsBucksWagerFinalizationState(
			bOddsBucksQaSlot,
			PersistedLedger,
			PersistedNextJobPayoutUnixSeconds,
			PersistedRequests,
			PersistedLocks,
			PersistedResults,
			PersistedDecisions,
			PersistedLossFinalizations,
			PersistedWinFinalizations,
			bPersistedFound,
			Error)
		&& bPersistedFound
		&& PersistedLedger.GetEntries().Num() == 2
		&& PersistedLedger.GetBalance() == 60
		&& PersistedRequests.Num() == 1
		&& PersistedLocks.Num() == 1
		&& PersistedResults.Num() == 1
		&& PersistedDecisions.IsEmpty()
		&& PersistedLossFinalizations.IsEmpty()
		&& PersistedWinFinalizations.IsEmpty()
		&& IsSameCanonicalMatchWinnerResultLink(
			PersistedResults[0],
			LinkedResult);
	if (!bDurable)
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_RESULT_LINK|result=REJECTED|phase=H26AE|reason=durable_reload_failed|booth=locked|mutation=unchanged_or_fail_closed|polling=false|timer=false|watcher=false|process=false|h26m_to_h26p=false|detail=%s"),
			*Error);
		return;
	}

	OddsBucksLedger = MoveTemp(PersistedLedger);
	NextJobPayoutUnixSeconds = PersistedNextJobPayoutUnixSeconds;
	MatchWinnerRequestCount = PersistedRequests.Num();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_RESULT_LINK|result=PASS|phase=H26AE|transition=%s|trigger=authoritative_local_resume|result_command=%s|request_command=%s|lock_command=%s|score=%d-%d|winner=%s|replay_sha256=%s|ledger_entries=2|balance=60|requests=1|locks=1|results=1|next=automatic_selection_owned_decision|h26n_to_h26p=false|booth=locked|polling=false|timer=false|watcher=false|process=false|cost_usd=0"),
		Transition == EOddsWellMatchWinnerResultLinkResult::Linked
			? TEXT("Linked")
			: TEXT("Duplicate"),
		*LinkedResult.ResultCommandId,
		*LinkedResult.RequestCommandId,
		*LinkedResult.LockCommandId,
		LinkedResult.HomeScore,
		LinkedResult.AwayScore,
		*LinkedResult.Winner,
		*LinkedResult.ReplaySealSha256);
	ResumeCanonicalMatchWinnerDecision(false);
}

bool AOddsWellLocomotionGameMode::ResumeCanonicalMatchWinnerDecision(
	const bool bRequireDuplicate)
{
	FOddsWellOddsBucksLedger LoadedLedger;
	int64 LoadedNextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> LoadedRequests;
	bool bLoadedFound = false;
	FString LoadError;
	if (!LoadOddsWellOddsBucksState(
			bOddsBucksQaSlot,
			LoadedLedger,
			LoadedNextJobPayoutUnixSeconds,
			LoadedRequests,
			bLoadedFound,
			LoadError)
		|| !bLoadedFound
		|| LoadedRequests.Num() != 1)
	{
		bOddsBucksReady = false;
		return false;
	}
	if (LoadedRequests[0].OfferedTeam == TEXT("Mesa Vista Sol"))
	{
		return ResumeCanonicalMatchWinnerMesaWinDecision(
			bRequireDuplicate);
	}

	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	FString Error;
	const EOddsWellMatchWinnerSettlementDecisionResult Transition =
		DecideOddsWellCanonicalMatchWinnerLossDecision(
			Decision,
			Error);
	if (Transition == EOddsWellMatchWinnerSettlementDecisionResult::Rejected)
	{
		if (bRequireDuplicate
			&& CanResumeCanonicalLossFinalizationAfterDecisionRejection(
				Error))
		{
			return ResumeCanonicalMatchWinnerLossFinalization(true);
		}
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_DECISION|result=REJECTED|phase=H26AF|reason=decision_rejected_or_non_exact|booth=locked|mutation=unchanged_or_fail_closed|h26n_to_h26p=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}
	if ((bRequireDuplicate
			&& Transition
				!= EOddsWellMatchWinnerSettlementDecisionResult::Duplicate)
		|| !IsExactCurrentCanonicalMatchWinnerLossDecision(Decision))
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_DECISION|result=REJECTED|phase=H26AF|reason=decision_rejected_or_non_exact|booth=locked|mutation=unchanged_or_fail_closed|h26n_to_h26p=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}

	FOddsWellOddsBucksLedger PersistedLedger;
	int64 PersistedNextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> PersistedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> PersistedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> PersistedResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> PersistedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord>
		PersistedLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord>
		PersistedWinFinalizations;
	bool bPersistedFound = false;
	const bool bDurable =
		LoadOddsWellOddsBucksWagerFinalizationState(
			bOddsBucksQaSlot,
			PersistedLedger,
			PersistedNextJobPayoutUnixSeconds,
			PersistedRequests,
			PersistedLocks,
			PersistedResults,
			PersistedDecisions,
			PersistedLossFinalizations,
			PersistedWinFinalizations,
			bPersistedFound,
			Error)
		&& bPersistedFound
		&& PersistedLedger.GetEntries().Num() == 2
		&& PersistedLedger.GetBalance() == 60
		&& PersistedRequests.Num() == 1
		&& PersistedLocks.Num() == 1
		&& PersistedResults.Num() == 1
		&& PersistedDecisions.Num() == 1
		&& PersistedLossFinalizations.IsEmpty()
		&& PersistedWinFinalizations.IsEmpty()
		&& IsExactCurrentCanonicalMatchWinnerResultLink(
			PersistedResults[0])
		&& IsExactCurrentCanonicalMatchWinnerLossDecision(
			PersistedDecisions[0]);
	if (!bDurable)
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_DECISION|result=REJECTED|phase=H26AF|reason=durable_reload_failed|booth=locked|mutation=unchanged_or_fail_closed|h26n_to_h26p=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}

	OddsBucksLedger = MoveTemp(PersistedLedger);
	NextJobPayoutUnixSeconds = PersistedNextJobPayoutUnixSeconds;
	MatchWinnerRequestCount = PersistedRequests.Num();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_DECISION|result=PASS|phase=H26AF|transition=%s|trigger=durable_h26l_local_resume|decision_command=%s|result_command=%s|selected_team=%s|winner=%s|stake=%lld|outcome=%s|gross_return_due=%lld|status=%s|ledger_entries=2|balance=60|requests=1|locks=1|results=1|decisions=1|loss_finalizations=0|win_finalizations=0|next=automatic_h26n|h26o_to_h26p=false|booth=locked|polling=false|timer=false|watcher=false|process=false|cost_usd=0"),
		Transition == EOddsWellMatchWinnerSettlementDecisionResult::Decided
			? TEXT("Decided")
			: TEXT("Duplicate"),
		*Decision.DecisionCommandId,
		*Decision.ResultCommandId,
		*Decision.SelectedTeam,
		*Decision.AuthoritativeWinner,
		Decision.Stake,
		*Decision.Outcome.ToString(),
		Decision.GrossReturnDue,
		*Decision.Status.ToString());
	return ResumeCanonicalMatchWinnerLossFinalization(false);
}

bool AOddsWellLocomotionGameMode::ResumeCanonicalMatchWinnerMesaWinDecision(
	const bool bRequireDuplicate)
{
	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	FString Error;
	const EOddsWellMatchWinnerSettlementDecisionResult Transition =
		DecideOddsWellCanonicalMatchWinnerCurrentMesaWinDecision(
			Decision,
			Error);
	if (Transition == EOddsWellMatchWinnerSettlementDecisionResult::Rejected
		|| (bRequireDuplicate
			&& Transition
				!= EOddsWellMatchWinnerSettlementDecisionResult::Duplicate)
		|| !IsExactCurrentCanonicalMatchWinnerMesaWinDecision(Decision))
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_MESA_WIN_DECISION|result=REJECTED|phase=H26AN|reason=decision_rejected_or_non_exact|booth=locked|mutation=unchanged_or_fail_closed|payout=false|finalization=false|reconciliation=false|receipt=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}

	FOddsWellOddsBucksLedger PersistedLedger;
	int64 PersistedNextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> PersistedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> PersistedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> PersistedResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> PersistedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord>
		PersistedLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord>
		PersistedWinFinalizations;
	bool bPersistedFound = false;
	const bool bDurable =
		LoadOddsWellOddsBucksWagerFinalizationState(
			bOddsBucksQaSlot,
			PersistedLedger,
			PersistedNextJobPayoutUnixSeconds,
			PersistedRequests,
			PersistedLocks,
			PersistedResults,
			PersistedDecisions,
			PersistedLossFinalizations,
			PersistedWinFinalizations,
			bPersistedFound,
			Error)
		&& bPersistedFound
		&& PersistedLedger.GetEntries().Num() == 2
		&& PersistedLedger.GetEntries()[0].Delta == 100
		&& PersistedLedger.GetEntries()[1].Delta == -40
		&& PersistedLedger.GetBalance() == 60
		&& PersistedRequests.Num() == 1
		&& PersistedRequests[0].OfferedTeam == TEXT("Mesa Vista Sol")
		&& PersistedLocks.Num() == 1
		&& PersistedResults.Num() == 1
		&& PersistedDecisions.Num() == 1
		&& PersistedLossFinalizations.IsEmpty()
		&& PersistedWinFinalizations.IsEmpty()
		&& IsExactCurrentCanonicalMatchWinnerResultLink(
			PersistedResults[0])
		&& IsExactCurrentCanonicalMatchWinnerMesaWinDecision(
			PersistedDecisions[0]);
	if (!bDurable)
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_MESA_WIN_DECISION|result=REJECTED|phase=H26AN|reason=durable_reload_failed|booth=locked|mutation=unchanged_or_fail_closed|payout=false|finalization=false|reconciliation=false|receipt=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}

	OddsBucksLedger = MoveTemp(PersistedLedger);
	NextJobPayoutUnixSeconds = PersistedNextJobPayoutUnixSeconds;
	MatchWinnerRequestCount = PersistedRequests.Num();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_MESA_WIN_DECISION|result=PASS|phase=H26AN|transition=%s|trigger=durable_h26l_local_resume|decision_command=%s|result_command=%s|selected_team=%s|winner=%s|stake=%lld|outcome=%s|probability_e8=%lld|gross_return_due=%lld|status=%s|ledger_entries=2|ledger_delta=-40|balance=60|requests=1|locks=1|results=1|decisions=1|loss_finalizations=0|win_finalizations=0|payout=false|reconciliation=false|receipt=false|booth=locked|polling=false|timer=false|watcher=false|process=false|cost_usd=0"),
		Transition == EOddsWellMatchWinnerSettlementDecisionResult::Decided
			? TEXT("Decided")
			: TEXT("Duplicate"),
		*Decision.DecisionCommandId,
		*Decision.ResultCommandId,
		*Decision.SelectedTeam,
		*Decision.AuthoritativeWinner,
		Decision.Stake,
		*Decision.Outcome.ToString(),
		Decision.SelectedWinProbabilityE8,
		Decision.GrossReturnDue,
		*Decision.Status.ToString());
	return true;
}

bool AOddsWellLocomotionGameMode::ResumeCanonicalMatchWinnerLossFinalization(
	const bool bRequireDuplicate)
{
	FOddsWellMatchWinnerLossFinalizationRecord Finalization;
	FString Error;
	const EOddsWellMatchWinnerLossFinalizationResult Transition =
		FinalizeOddsWellCanonicalMatchWinnerLoss(
			Finalization,
			Error);
	if (Transition == EOddsWellMatchWinnerLossFinalizationResult::Rejected
		|| (bRequireDuplicate
			&& Transition
				!= EOddsWellMatchWinnerLossFinalizationResult::Duplicate)
		|| !IsExactCurrentCanonicalMatchWinnerLossFinalization(
			Finalization))
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_FINALIZATION|result=REJECTED|phase=H26AG|reason=finalization_rejected_or_non_exact|booth=locked|mutation=unchanged_or_fail_closed|h26o_to_h26p=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}

	FOddsWellOddsBucksLedger PersistedLedger;
	int64 PersistedNextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> PersistedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> PersistedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> PersistedResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> PersistedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord>
		PersistedLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord>
		PersistedWinFinalizations;
	bool bPersistedFound = false;
	const bool bDurable =
		LoadOddsWellOddsBucksWagerFinalizationState(
			bOddsBucksQaSlot,
			PersistedLedger,
			PersistedNextJobPayoutUnixSeconds,
			PersistedRequests,
			PersistedLocks,
			PersistedResults,
			PersistedDecisions,
			PersistedLossFinalizations,
			PersistedWinFinalizations,
			bPersistedFound,
			Error)
		&& bPersistedFound
		&& PersistedLedger.GetEntries().Num() == 2
		&& PersistedLedger.GetEntries()[0].Delta == 100
		&& PersistedLedger.GetEntries()[0].BalanceAfter == 100
		&& PersistedLedger.GetEntries()[1].Delta == -40
		&& PersistedLedger.GetEntries()[1].BalanceAfter == 60
		&& PersistedLedger.GetBalance() == 60
		&& PersistedRequests.Num() == 1
		&& PersistedLocks.Num() == 1
		&& PersistedResults.Num() == 1
		&& PersistedDecisions.Num() == 1
		&& PersistedLossFinalizations.Num() == 1
		&& PersistedWinFinalizations.IsEmpty()
		&& IsExactCurrentCanonicalMatchWinnerResultLink(
			PersistedResults[0])
		&& IsExactCurrentCanonicalMatchWinnerLossDecision(
			PersistedDecisions[0])
		&& IsExactCurrentCanonicalMatchWinnerLossFinalization(
			PersistedLossFinalizations[0]);
	if (!bDurable)
	{
		bOddsBucksReady = false;
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_FINALIZATION|result=REJECTED|phase=H26AG|reason=durable_reload_or_projection_failed|booth=locked|mutation=unchanged_or_fail_closed|h26o_to_h26p=false|polling=false|timer=false|watcher=false|process=false|detail=%s"),
			*Error);
		return false;
	}

	OddsBucksLedger = MoveTemp(PersistedLedger);
	NextJobPayoutUnixSeconds = PersistedNextJobPayoutUnixSeconds;
	MatchWinnerRequestCount = PersistedRequests.Num();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_LOSS_FINALIZATION|result=PASS|phase=H26AG|transition=%s|trigger=durable_h26m_local_resume|finalization_command=%s|decision_command=%s|result_command=%s|selected_team=%s|winner=%s|stake=%lld|outcome=%s|gross_return_due=0|gross_return_applied=%lld|status=%s|ledger_entries=2|ledger_delta=-40|balance=60|requests=1|locks=1|results=1|decisions=1|loss_finalizations=1|win_finalizations=0|reconciliation_projection=regenerated_by_existing_h26n_loader|h26o_to_h26p=false|booth=locked|polling=false|timer=false|watcher=false|process=false|cost_usd=0"),
		Transition == EOddsWellMatchWinnerLossFinalizationResult::Finalized
			? TEXT("Finalized")
			: TEXT("Duplicate"),
		*Finalization.FinalizationCommandId,
		*Finalization.DecisionCommandId,
		*Finalization.ResultCommandId,
		*Finalization.SelectedTeam,
		*Finalization.AuthoritativeWinner,
		Finalization.Stake,
		*Finalization.Outcome.ToString(),
		Finalization.GrossReturnApplied,
		*Finalization.Status.ToString());
	return true;
}

void AOddsWellLocomotionGameMode::ScheduleCanonicalMatchWinnerTipoffLock()
{
	if (!bOddsBucksReady || !GetWorld())
	{
		return;
	}
	FOddsWellCanonicalPendingMatchWinnerReceipt Receipt;
	FString Error;
	if (LoadOddsWellCanonicalPendingMatchWinnerReceipt(Receipt, Error)
		!= EOddsWellCanonicalPendingReceiptResult::Ready)
	{
		return;
	}
	const int64 NowUnixSeconds = FDateTime::UtcNow().ToUnixTimestamp();
	if (!ShouldScheduleCanonicalMatchWinnerTipoffLock(
			GetWorldTimerManager().TimerExists(
				CanonicalMatchWinnerTipoffLockTimer),
			NowUnixSeconds,
			Receipt.LockUnixSeconds))
	{
		return;
	}
	const bool bQaDelay =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQa"))
		|| FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQaVerify"));
	const double DelaySeconds = bQaDelay
		? 4.0
		: (FDateTime::FromUnixTimestamp(Receipt.LockUnixSeconds)
			- FDateTime::UtcNow()).GetTotalSeconds();
	if (DelaySeconds <= 0.0)
	{
		return;
	}
	GetWorldTimerManager().SetTimer(
		CanonicalMatchWinnerTipoffLockTimer,
		this,
		&AOddsWellLocomotionGameMode::RunCanonicalMatchWinnerTipoffLock,
		static_cast<float>(DelaySeconds),
		false);
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_TIPOFF_LOCK|result=SCHEDULED|timer=one|loop=false|tipoff_unix=%lld|qa_delay=%s|caller_time=false|caller_identity=false|catch_up=false"),
		Receipt.LockUnixSeconds,
		bQaDelay ? TEXT("true") : TEXT("false"));
}

void AOddsWellLocomotionGameMode::RunCanonicalMatchWinnerTipoffLock()
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FString Error;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, Error))
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_TIPOFF_LOCK|result=REJECTED|reason=schedule_invalid|mutation=false|detail=%s"),
			*Error);
		return;
	}
	const bool bQaClock =
		FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQa"))
		|| FParse::Param(
			FCommandLine::Get(),
			TEXT("CanonicalAutomaticTipoffLockQaVerify"));
	const int64 ObservedServerUnixSeconds = bQaClock
		? Schedule.TipoffUnixSeconds
		: FDateTime::UtcNow().ToUnixTimestamp();
	if (!IsExactCanonicalMatchWinnerTipoff(
			ObservedServerUnixSeconds,
			Schedule.TipoffUnixSeconds))
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_TIPOFF_LOCK|result=REJECTED|reason=not_exact_tipoff|observed_unix=%lld|tipoff_unix=%lld|backdated=false|catch_up=false|mutation=false"),
			ObservedServerUnixSeconds,
			Schedule.TipoffUnixSeconds);
		return;
	}
	FOddsWellMatchWinnerLockRecord Lock;
	const EOddsWellMatchWinnerLockResult Result =
		LockOddsWellCanonicalMatchWinnerRequestAtGameStart(Lock, Error);
	FOddsWellOddsBucksLedger PersistedLedger;
	int64 PersistedNextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	bool bFound = false;
	const bool bDurable =
		(Result == EOddsWellMatchWinnerLockResult::Locked
			|| Result == EOddsWellMatchWinnerLockResult::Duplicate)
		&& LoadOddsWellOddsBucksWagerEvidence(
			bOddsBucksQaSlot,
			PersistedLedger,
			PersistedNextJobPayoutUnixSeconds,
			Requests,
			Locks,
			Results,
			bFound,
			Error)
		&& bFound
		&& PersistedLedger.GetEntries().Num() == 2
		&& PersistedLedger.GetEntries()[0].Delta == 100
		&& PersistedLedger.GetEntries()[1].Delta == -40
		&& PersistedLedger.GetBalance() == 60
		&& Requests.Num() == 1
		&& Locks.Num() == 1
		&& Results.IsEmpty()
		&& Requests[0].RequestCommandId == Lock.RequestCommandId
		&& Requests[0].OfferedTeam == TEXT("Harbor City Waves")
		&& Requests[0].Stake == 40
		&& Requests[0].Status == FName(TEXT("accepted_pending_lock"))
		&& Locks[0].LockCommandId == Lock.LockCommandId
		&& Locks[0].Decision == FName(TEXT("locked"));
	if (!bDurable)
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_TIPOFF_LOCK|result=REJECTED|reason=lock_or_reload_failed|mutation=unchanged_or_fail_closed|detail=%s"),
			*Error);
		return;
	}
	OddsBucksLedger = MoveTemp(PersistedLedger);
	NextJobPayoutUnixSeconds = PersistedNextJobPayoutUnixSeconds;
	MatchWinnerRequestCount = Requests.Num();
	PublishOddsBucksReconciliation();
	for (TActorIterator<AOddsWellPlaceholderCharacter> It(GetWorld()); It; ++It)
	{
		It->RefreshTicketBoothAfterCanonicalLock();
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_TIPOFF_LOCK|result=PASS|transition=%s|timer=one|loop=false|clock=exact_h26a_tipoff|locks=1|requests=1|ledger_entries=2|balance=60|request_unchanged=true|ui_refreshed_after_durable_success=true|next=automatic_h26h|catch_up=false|backdated=false"),
		Result == EOddsWellMatchWinnerLockResult::Locked
			? TEXT("locked")
			: TEXT("duplicate"));

	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
	const EOddsWellCanonicalActiveGameExecutionCommitmentResult
		CommitmentResult =
			CreateOddsWellCanonicalActiveGameExecutionCommitment(
				Commitment,
				Error);
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord
		ReloadedCommitment;
	const bool bCommitmentDurable =
		(CommitmentResult
				== EOddsWellCanonicalActiveGameExecutionCommitmentResult::Created
			|| CommitmentResult
				== EOddsWellCanonicalActiveGameExecutionCommitmentResult::Duplicate)
		&& LoadOddsWellCanonicalActiveGameExecutionCommitment(
			ReloadedCommitment,
			Error)
		&& ReloadedCommitment.Schema
			== TEXT("oddswell-canonical-active-game-execution-commitment-v1")
		&& ReloadedCommitment.RecordVersion == 1
		&& ReloadedCommitment.Status == TEXT("committed_for_execution")
		&& ReloadedCommitment.SeedMaterialSha256
			== Commitment.SeedMaterialSha256
		&& ReloadedCommitment.ExecutionInputSha256
			== Commitment.ExecutionInputSha256
		&& ReloadedCommitment.CommitmentSha256
			== Commitment.CommitmentSha256;
	if (!bCommitmentDurable)
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_EXECUTION_COMMITMENT|result=REJECTED|phase=H26T|reason=create_or_reload_failed|lock_retained=true|booth=locked|private_seed=true|private_input=true|public_surface=false|h26i_to_h26p=false"));
		return;
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_EXECUTION_COMMITMENT|result=PASS|phase=H26T|transition=%s|trigger=durably_reloaded_h26g|schema=oddswell-canonical-active-game-execution-commitment-v1|record_version=1|status=committed_for_execution|commitments=1|locks=1|requests=1|ledger_entries=2|balance=60|booth=locked|private_seed=true|private_input=true|public_surface=false|caller_seed=false|caller_input=false|caller_time=false|caller_path=false|simulation=false|result_state=false|next=automatic_h26i|settlement=false"),
		CommitmentResult
				== EOddsWellCanonicalActiveGameExecutionCommitmentResult::Created
			? TEXT("created")
			: TEXT("duplicate"));

	FString HandoffPath;
	FString HandoffSha256;
	const EOddsWellCanonicalGameExecutionHandoffResult HandoffResult =
		WriteOddsWellCanonicalGameExecutionHandoff(
			HandoffPath,
			HandoffSha256,
			Error);
	const bool bHandoffDurable =
		(HandoffResult
				== EOddsWellCanonicalGameExecutionHandoffResult::Created
			|| HandoffResult
				== EOddsWellCanonicalGameExecutionHandoffResult::Duplicate)
		&& HandoffPath == GetCanonicalGameExecutionHandoffPath()
		&& HandoffSha256.Len() == 64
		&& IFileManager::Get().FileSize(*HandoffPath) > 0;
	if (!bHandoffDurable)
	{
		UE_LOG(
			LogOddsWellLocomotion,
			Error,
			TEXT("ODDSWELL_CANONICAL_AUTOMATIC_EXECUTION_HANDOFF|result=REJECTED|phase=H26U|reason=create_or_exact_duplicate_failed|lock_retained=true|commitment_retained=true|booth=locked|private=true|public_surface=false|python_consumer=false|receipt=false|h26j_to_h26p=false"));
		return;
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_CANONICAL_AUTOMATIC_EXECUTION_HANDOFF|result=PASS|phase=H26U|transition=%s|trigger=durably_reloaded_h26h|handoffs=1|commitments=1|locks=1|requests=1|ledger_entries=2|balance=60|booth=locked|private=true|public_surface=false|fixed_path=true|caller_seed=false|caller_input=false|caller_time=false|caller_path=false|python_consumer=false|process=false|receipt=false|simulation=false|seal=false|result_state=false|settlement=false"),
		HandoffResult
				== EOddsWellCanonicalGameExecutionHandoffResult::Created
			? TEXT("created")
			: TEXT("duplicate"));
}

bool AOddsWellLocomotionGameMode::RunSportsbookQaWagerAudit(
	int32& OutLedgerEntries,
	int32& OutRequests,
	int64& OutBalance,
	FString& OutError)
{
	if (!bOddsBucksQaSlot || !bSportsbookWagerQa || GetNetMode() != NM_Standalone
		|| !RunOddsWellUpcomingQaMatchWinnerAudit(OutLedgerEntries, OutRequests, OutBalance, OutError))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The isolated machine-local Sportsbook QA audit is unavailable.");
		}
		return false;
	}
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	bool bFound = false;
	if (!LoadOddsWellOddsBucksState(true, OddsBucksLedger, NextJobPayoutUnixSeconds, Requests, bFound, OutError) || !bFound)
	{
		return false;
	}
	MatchWinnerRequestCount = Requests.Num();
	return true;
}

void AOddsWellLocomotionGameMode::RunSportsbookLockQa()
{
	if (bSportsbookLockQaDone)
	{
		return;
	}
	const int64 LockUnixSeconds = GetOddsWellUpcomingQaMatchWinnerLockUnixSeconds();
	if (!bOddsBucksReady || !bOddsBucksQaSlot || GetNetMode() != NM_Standalone)
	{
		bSportsbookLockQaDone = true;
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_LOCK_QA|result=FAIL|reason=authority_unavailable"));
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (SportsbookLockQaStage == 0)
	{
		if (GetOddsBucksNowUnixSeconds() != LockUnixSeconds - 1
			|| !AdvanceOddsBucksQaClock(1))
		{
			bSportsbookLockQaDone = true;
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_LOCK_QA|result=FAIL|reason=early_gate"));
			FPlatformMisc::RequestExit(false);
			return;
		}
		SportsbookLockQaStage = 1;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SPORTSBOOK_LOCK_GATE|result=PASS|before_start_transition=false|server_clock_advanced=true|now_unix=%lld"), GetOddsBucksNowUnixSeconds());
		return;
	}
	if (GetOddsBucksNowUnixSeconds() != LockUnixSeconds)
	{
		bSportsbookLockQaDone = true;
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_LOCK_QA|result=FAIL|reason=clock_mismatch|now_unix=%lld|lock_unix=%lld"), GetOddsBucksNowUnixSeconds(), LockUnixSeconds);
		FPlatformMisc::RequestExit(false);
		return;
	}

	FOddsWellMatchWinnerLockRecord Lock;
	FString Error;
	const EOddsWellMatchWinnerLockResult Result =
		LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Lock, Error);
	int32 Entries = 2;
	int32 Requests = 1;
	int32 Locks = 1;
	int64 Balance = 60;
	bool bPassed = bSportsbookLockQaVerify
		? Result == EOddsWellMatchWinnerLockResult::Duplicate
			&& RunOddsWellUpcomingQaMatchWinnerLockAudit(Entries, Requests, Locks, Balance, Error)
		: Result == EOddsWellMatchWinnerLockResult::Locked;
	bool bCleanup = true;
	if (bSportsbookLockQaVerify)
	{
		FString CleanupError;
		bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
		if (!bCleanup && Error.IsEmpty())
		{
			Error = CleanupError;
		}
		bPassed = bPassed && bCleanup;
	}
	bPassed = bPassed
		&& Lock.LockCommandId == GetOddsWellUpcomingQaMatchWinnerLockCommandId()
		&& Lock.RequestCommandId == GetOddsWellUpcomingQaMatchWinnerRequestCommandId()
		&& Lock.SeasonNumber == 100
		&& Lock.GameNumber == 1
		&& Lock.AuthoritativeGameStartUnixSeconds == LockUnixSeconds
		&& Lock.LockUnixSeconds == LockUnixSeconds
		&& Entries == 2
		&& Requests == 1
		&& Locks == 1
		&& Balance == 60;
	bSportsbookLockQaDone = true;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_SPORTSBOOK_LOCK_QA|result=%s|cold_process_restore=%s|server_owned=true|client_command=false|request_id=%s|lock_command_id=%s|season=100|game=1|authoritative_start_unix=%lld|decision=locked|exact_retry=%s|rejection_audit=%s|zero_mutation=%s|ledger_entries=%d|requests=%d|locks=%d|balance=%lld|score=false|winner=false|replay=false|simulation=false|settlement=false|cleanup=%s|detail=%s"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		bSportsbookLockQaVerify ? TEXT("true") : TEXT("false"),
		*GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerLockCommandId(),
		LockUnixSeconds,
		bSportsbookLockQaVerify ? TEXT("duplicate") : TEXT("not_run"),
		bSportsbookLockQaVerify ? TEXT("wrong_request,wrong_game,early,late,conflict,second_lock,completed_h16,invented_time") : TEXT("deferred"),
		bSportsbookLockQaVerify ? TEXT("true") : TEXT("not_claimed"),
		Entries,
		Requests,
		Locks,
		Balance,
		bSportsbookLockQaVerify ? (bCleanup ? TEXT("true") : TEXT("false")) : TEXT("deferred"),
		Error.IsEmpty() ? TEXT("none") : *Error);
	if (bPassed)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	FPlatformMisc::RequestExit(false);
}

void AOddsWellLocomotionGameMode::RunSportsbookCancellationQa()
{
	if (bSportsbookCancellationQaDone)
	{
		return;
	}
	const int64 CancellationUnixSeconds = GetOddsWellUpcomingQaMatchWinnerCancellationUnixSeconds();
	if (!bOddsBucksReady || !bOddsBucksQaSlot || GetNetMode() != NM_Standalone)
	{
		bSportsbookCancellationQaDone = true;
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_CANCELLATION_QA|result=FAIL|reason=authority_unavailable"));
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (SportsbookCancellationQaStage == 0)
	{
		if (GetOddsBucksNowUnixSeconds() != CancellationUnixSeconds - 1
			|| !AdvanceOddsBucksQaClock(1))
		{
			bSportsbookCancellationQaDone = true;
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_CANCELLATION_QA|result=FAIL|reason=pre_cancellation_gate"));
			FPlatformMisc::RequestExit(false);
			return;
		}
		SportsbookCancellationQaStage = 1;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SPORTSBOOK_CANCELLATION_GATE|result=PASS|post_lock=true|server_clock_advanced=true|now_unix=%lld"), GetOddsBucksNowUnixSeconds());
		return;
	}
	if (GetOddsBucksNowUnixSeconds() != CancellationUnixSeconds)
	{
		bSportsbookCancellationQaDone = true;
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_CANCELLATION_QA|result=FAIL|reason=clock_mismatch|now_unix=%lld|cancellation_unix=%lld"), GetOddsBucksNowUnixSeconds(), CancellationUnixSeconds);
		FPlatformMisc::RequestExit(false);
		return;
	}

	FOddsWellMatchWinnerCanceledGameRecord Cancellation;
	FString Error;
	const EOddsWellMatchWinnerCanceledGameResult Result =
		RecordOddsWellUpcomingQaMatchWinnerCancellation(Cancellation, Error);
	int32 Entries = 2;
	int32 Requests = 1;
	int32 Locks = 1;
	int32 Cancellations = 1;
	int64 Balance = 60;
	bool bPassed = bSportsbookCancellationQaVerify
		? Result == EOddsWellMatchWinnerCanceledGameResult::Duplicate
			&& RunOddsWellUpcomingQaMatchWinnerCancellationAudit(
				Entries,
				Requests,
				Locks,
				Cancellations,
				Balance,
				Error)
		: Result == EOddsWellMatchWinnerCanceledGameResult::Recorded;
	bool bCleanup = true;
	if (bSportsbookCancellationQaVerify)
	{
		FString CleanupError;
		bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
		if (!bCleanup && Error.IsEmpty())
		{
			Error = CleanupError;
		}
		bPassed = bPassed && bCleanup;
	}
	bPassed = bPassed
		&& Cancellation.CancellationCommandId == GetOddsWellUpcomingQaMatchWinnerCancellationCommandId()
		&& Cancellation.CancellationEvidenceId == GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId()
		&& Cancellation.RequestCommandId == GetOddsWellUpcomingQaMatchWinnerRequestCommandId()
		&& Cancellation.LockCommandId == GetOddsWellUpcomingQaMatchWinnerLockCommandId()
		&& Cancellation.SeasonNumber == 100
		&& Cancellation.GameNumber == 1
		&& Cancellation.AuthoritativeCancellationUnixSeconds == CancellationUnixSeconds
		&& Cancellation.ReasonCode == FName(TEXT("game_canceled"))
		&& Cancellation.Status == FName(TEXT("closed_canceled"))
		&& Entries == 2
		&& Requests == 1
		&& Locks == 1
		&& Cancellations == 1
		&& Balance == 60;
	bSportsbookCancellationQaDone = true;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_SPORTSBOOK_CANCELLATION_QA|result=%s|cold_process_restore=%s|server_owned=true|client_command=false|request_id=%s|lock_command_id=%s|cancellation_command_id=%s|cancellation_evidence_id=%s|season=100|game=1|authoritative_cancellation_unix=%lld|reason=game_canceled|status=closed_canceled|exact_retry=%s|rejection_audit=%s|zero_mutation=%s|ledger_entries=%d|requests=%d|locks=%d|cancellations=%d|balance=%lld|score=false|winner=false|replay=false|normal_result=false|settlement=false|refund_decision=false|credit=false|finalization=false|cleanup=%s|detail=%s"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		bSportsbookCancellationQaVerify ? TEXT("true") : TEXT("false"),
		*GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerLockCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerCancellationCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId(),
		CancellationUnixSeconds,
		bSportsbookCancellationQaVerify ? TEXT("duplicate") : TEXT("not_run"),
		bSportsbookCancellationQaVerify ? TEXT("wrong_request,wrong_lock,wrong_game,wrong_time,wrong_evidence,conflict,second,malformed,normal_result,completed_h16") : TEXT("deferred"),
		bSportsbookCancellationQaVerify ? TEXT("true") : TEXT("not_claimed"),
		Entries,
		Requests,
		Locks,
		Cancellations,
		Balance,
		bSportsbookCancellationQaVerify ? (bCleanup ? TEXT("true") : TEXT("false")) : TEXT("deferred"),
		Error.IsEmpty() ? TEXT("none") : *Error);
	if (bPassed)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	FPlatformMisc::RequestExit(false);
}

void AOddsWellLocomotionGameMode::RunSportsbookVoidDecisionQa()
{
	if (bSportsbookVoidDecisionQaDone)
	{
		return;
	}
	if (!bOddsBucksReady || !bOddsBucksQaSlot || GetNetMode() != NM_Standalone)
	{
		bSportsbookVoidDecisionQaDone = true;
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_VOID_DECISION_QA|result=FAIL|reason=authority_unavailable"));
		FPlatformMisc::RequestExit(false);
		return;
	}

	FOddsWellMatchWinnerVoidDecisionRecord Decision;
	FString Error;
	const EOddsWellMatchWinnerVoidDecisionResult Result =
		DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(Decision, Error);
	int32 Entries = 2;
	int32 Requests = 1;
	int32 Locks = 1;
	int32 Cancellations = 1;
	int32 VoidDecisions = 1;
	int64 Balance = 60;
	bool bPassed = bSportsbookVoidDecisionQaVerify
		? Result == EOddsWellMatchWinnerVoidDecisionResult::Duplicate
			&& RunOddsWellUpcomingQaMatchWinnerVoidDecisionAudit(
				Entries,
				Requests,
				Locks,
				Cancellations,
				VoidDecisions,
				Balance,
				Error)
		: Result == EOddsWellMatchWinnerVoidDecisionResult::Decided;
	bool bCleanup = true;
	if (bSportsbookVoidDecisionQaVerify)
	{
		FString CleanupError;
		bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
		if (!bCleanup && Error.IsEmpty())
		{
			Error = CleanupError;
		}
		bPassed = bPassed && bCleanup;
	}
	bPassed = bPassed
		&& Decision.VoidDecisionCommandId == GetOddsWellUpcomingQaMatchWinnerVoidDecisionCommandId()
		&& Decision.CancellationCommandId == GetOddsWellUpcomingQaMatchWinnerCancellationCommandId()
		&& Decision.CancellationEvidenceId == GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId()
		&& Decision.RequestCommandId == GetOddsWellUpcomingQaMatchWinnerRequestCommandId()
		&& Decision.LockCommandId == GetOddsWellUpcomingQaMatchWinnerLockCommandId()
		&& Decision.SeasonNumber == 100
		&& Decision.GameNumber == 1
		&& Decision.SelectedTeam == TEXT("Sundale Sparks")
		&& Decision.Stake == 40
		&& Decision.CancellationReason == FName(TEXT("game_canceled"))
		&& Decision.Outcome == FName(TEXT("voided"))
		&& Decision.RefundDue == 40
		&& Decision.Status == FName(TEXT("decided_void_pending_refund"))
		&& Entries == 2
		&& Requests == 1
		&& Locks == 1
		&& Cancellations == 1
		&& VoidDecisions == 1
		&& Balance == 60;
	bSportsbookVoidDecisionQaDone = true;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_SPORTSBOOK_VOID_DECISION_QA|result=%s|cold_process_restore=%s|server_owned=true|client_command=false|decision_command_id=%s|request_id=%s|lock_command_id=%s|cancellation_command_id=%s|cancellation_evidence_id=%s|season=100|game=1|selected_team=Sundale Sparks|stake=40|outcome=voided|refund_due=40|status=decided_void_pending_refund|exact_retry=%s|rejection_audit=%s|zero_mutation=%s|ledger_entries=%d|requests=%d|locks=%d|cancellations=%d|void_decisions=%d|balance=%lld|result=false|replay=false|simulation=false|settlement=false|refund_applied=false|credit=false|finalization=false|cleanup=%s|detail=%s"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		bSportsbookVoidDecisionQaVerify ? TEXT("true") : TEXT("false"),
		*GetOddsWellUpcomingQaMatchWinnerVoidDecisionCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerLockCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerCancellationCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId(),
		bSportsbookVoidDecisionQaVerify ? TEXT("duplicate") : TEXT("not_run"),
		bSportsbookVoidDecisionQaVerify ? TEXT("wrong_link,wrong_evidence,conflict,second,malformed,normal_result") : TEXT("deferred"),
		bSportsbookVoidDecisionQaVerify ? TEXT("true") : TEXT("not_claimed"),
		Entries,
		Requests,
		Locks,
		Cancellations,
		VoidDecisions,
		Balance,
		bSportsbookVoidDecisionQaVerify ? (bCleanup ? TEXT("true") : TEXT("false")) : TEXT("deferred"),
		Error.IsEmpty() ? TEXT("none") : *Error);
	if (bPassed)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	FPlatformMisc::RequestExit(false);
}

void AOddsWellLocomotionGameMode::RunSportsbookVoidFinalizationQa()
{
	if (bSportsbookVoidFinalizationQaDone)
	{
		return;
	}
	if (!bOddsBucksReady || !bOddsBucksQaSlot || GetNetMode() != NM_Standalone)
	{
		bSportsbookVoidFinalizationQaDone = true;
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SPORTSBOOK_VOID_FINALIZATION_QA|result=FAIL|reason=authority_unavailable"));
		FPlatformMisc::RequestExit(false);
		return;
	}

	FOddsWellMatchWinnerVoidFinalizationRecord Finalization;
	FString Error;
	const EOddsWellMatchWinnerVoidFinalizationResult Result =
		FinalizeOddsWellUpcomingQaMatchWinnerVoidRefund(Finalization, Error);
	int32 Entries = 3;
	int32 Requests = 1;
	int32 Locks = 1;
	int32 Cancellations = 1;
	int32 VoidDecisions = 1;
	int32 VoidFinalizations = 1;
	int64 Balance = 100;
	bool bPassed = bSportsbookVoidFinalizationQaVerify
		? Result == EOddsWellMatchWinnerVoidFinalizationResult::Duplicate
			&& RunOddsWellUpcomingQaMatchWinnerVoidFinalizationAudit(
				Entries,
				Requests,
				Locks,
				Cancellations,
				VoidDecisions,
				VoidFinalizations,
				Balance,
				Error)
		: Result == EOddsWellMatchWinnerVoidFinalizationResult::Finalized;
	bool bCleanup = true;
	if (bSportsbookVoidFinalizationQaVerify)
	{
		FString CleanupError;
		bCleanup = ResetOddsWellQaOddsBucksAndVerify(CleanupError);
		if (!bCleanup && Error.IsEmpty())
		{
			Error = CleanupError;
		}
		bPassed = bPassed && bCleanup;
	}
	bPassed = bPassed
		&& Finalization.FinalizationCommandId == GetOddsWellUpcomingQaMatchWinnerVoidFinalizationCommandId()
		&& Finalization.VoidDecisionCommandId == GetOddsWellUpcomingQaMatchWinnerVoidDecisionCommandId()
		&& Finalization.CancellationCommandId == GetOddsWellUpcomingQaMatchWinnerCancellationCommandId()
		&& Finalization.CancellationEvidenceId == GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId()
		&& Finalization.RequestCommandId == GetOddsWellUpcomingQaMatchWinnerRequestCommandId()
		&& Finalization.LockCommandId == GetOddsWellUpcomingQaMatchWinnerLockCommandId()
		&& Finalization.SeasonNumber == 100
		&& Finalization.GameNumber == 1
		&& Finalization.SelectedTeam == TEXT("Sundale Sparks")
		&& Finalization.Stake == 40
		&& Finalization.CancellationReason == FName(TEXT("game_canceled"))
		&& Finalization.Outcome == FName(TEXT("voided"))
		&& Finalization.RefundDue == 40
		&& Finalization.RefundApplied == 40
		&& Finalization.RefundLedgerCommandId == GetOddsWellUpcomingQaMatchWinnerVoidFinalizationCommandId()
		&& Finalization.Status == FName(TEXT("settled_void"))
		&& Finalization.ObservedLedgerEntryCount == 3
		&& Finalization.ObservedFinalBalance == 100
		&& Entries == 3
		&& Requests == 1
		&& Locks == 1
		&& Cancellations == 1
		&& VoidDecisions == 1
		&& VoidFinalizations == 1
		&& Balance == 100;
	bSportsbookVoidFinalizationQaDone = true;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_SPORTSBOOK_VOID_FINALIZATION_QA|result=%s|cold_process_restore=%s|server_owned=true|client_command=false|finalization_command_id=%s|decision_command_id=%s|request_id=%s|lock_command_id=%s|cancellation_command_id=%s|cancellation_evidence_id=%s|season=100|game=1|selected_team=Sundale Sparks|stake=40|outcome=voided|refund_due=40|refund_applied=40|decision_status=decided_void_pending_refund|status=settled_void|exact_retry=%s|rejection_audit=%s|zero_mutation=%s|ledger_sequence=3|ledger_delta=40|ledger_entries=%d|requests=%d|locks=%d|cancellations=%d|void_decisions=%d|void_finalizations=%d|balance=%lld|result=false|replay=false|simulation=false|normal_settlement=false|history=true|ui=false|correction=false|cleanup=%s|detail=%s"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		bSportsbookVoidFinalizationQaVerify ? TEXT("true") : TEXT("false"),
		*GetOddsWellUpcomingQaMatchWinnerVoidFinalizationCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerVoidDecisionCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerLockCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerCancellationCommandId(),
		*GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId(),
		bSportsbookVoidFinalizationQaVerify ? TEXT("duplicate") : TEXT("not_run"),
		bSportsbookVoidFinalizationQaVerify ? TEXT("wrong_decision,wrong_link,conflict,second,tamper,normal_result,malformed,unexpected_ledger") : TEXT("deferred"),
		bSportsbookVoidFinalizationQaVerify ? TEXT("true") : TEXT("not_claimed"),
		Entries,
		Requests,
		Locks,
		Cancellations,
		VoidDecisions,
		VoidFinalizations,
		Balance,
		bSportsbookVoidFinalizationQaVerify ? (bCleanup ? TEXT("true") : TEXT("false")) : TEXT("deferred"),
		Error.IsEmpty() ? TEXT("none") : *Error);
	if (bPassed)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	FPlatformMisc::RequestExit(false);
}

void AOddsWellLocomotionGameMode::PostLogin(APlayerController* NewPlayer)
{
	Super::PostLogin(NewPlayer);
	if (GetNetMode() != NM_Standalone)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_JOIN|clients=%d|boundary=local_listen_server"), GetNumPlayers());
	}
}

void AOddsWellLocomotionGameMode::Logout(AController* Exiting)
{
	if (bSharedCityReconnectQa
		&& !bSharedCityReconnectPassed
		&& SharedCityReconnectExpectedAppearance.bOwnerSubmitted
		&& Exiting
		&& !Exiting->IsLocalController())
	{
		bSharedCityReconnectLeaveObserved = true;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_RECONNECT_LEAVE|player=Player_%d|preset=%s|top=%s|bottom=%s|captured=true"),
			SharedCityReconnectExpectedPlayerNumber,
			*SharedCityReconnectExpectedAppearance.PresetId.ToString(),
			*SharedCityReconnectExpectedAppearance.TopItemId.ToString(),
			*SharedCityReconnectExpectedAppearance.BottomItemId.ToString());
	}
	Super::Logout(Exiting);
	if (GetNetMode() != NM_Standalone)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_LEAVE|clients=%d"), GetNumPlayers());
	}
}

void AOddsWellLocomotionGameMode::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (SharedCityQaExitAt > 0.0 && FPlatformTime::Seconds() >= SharedCityQaExitAt)
	{
		SharedCityQaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bSportsbookLockQa)
	{
		RunSportsbookLockQa();
		return;
	}
	if (bSportsbookCancellationQa)
	{
		RunSportsbookCancellationQa();
		return;
	}
	if (bSportsbookVoidDecisionQa)
	{
		RunSportsbookVoidDecisionQa();
		return;
	}
	if (bSportsbookVoidFinalizationQa)
	{
		RunSportsbookVoidFinalizationQa();
		return;
	}
	if (!bSharedCityQa
		|| bSharedCityReconnectPassed
		|| (bSharedCityQaPassed && !bSharedCityReconnectQa && !bSharedCityCapacityQa))
	{
		return;
	}
	TArray<AOddsWellPlaceholderCharacter*> Players;
	for (TActorIterator<AOddsWellPlaceholderCharacter> It(GetWorld()); It; ++It)
	{
		if (It->GetSharedCityPlayerNumber() > 0)
		{
			Players.Add(*It);
		}
	}
	if (Players.Num() < SharedCityQaTargetClients)
	{
		return;
	}
	if (!bSharedCityQaStarted)
	{
		for (const AOddsWellPlaceholderCharacter* Player : Players)
		{
			SharedCityQaStartLocations.Add(Player->GetSharedCityPlayerNumber(), Player->GetActorLocation());
		}
		bSharedCityQaStarted = true;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_READY|clients=%d|map=%s|spawn_spacing=%.0f"), Players.Num(), *GetWorld()->GetMapName(), SharedCitySpawnSpacing);
		return;
	}
	const bool bAppearancesReady = !Players.ContainsByPredicate(
		[](const AOddsWellPlaceholderCharacter* Player)
		{
			return !Player->HasValidSharedCityAppearance() || !Player->HasSubmittedSharedCityAppearance();
		});
	if (bSharedCityCapacityQa && !bSharedCityQaPassed && bAppearancesReady)
	{
		int32 RemoteMovers = 0;
		float MinimumRemoteDistance = TNumericLimits<float>::Max();
		for (const AOddsWellPlaceholderCharacter* Player : Players)
		{
			if (Player->GetSharedCityPlayerNumber() <= 1)
			{
				continue;
			}
			const FVector* Start = SharedCityQaStartLocations.Find(Player->GetSharedCityPlayerNumber());
			const float Distance = Start ? FVector::Dist2D(*Start, Player->GetActorLocation()) : 0.0f;
			MinimumRemoteDistance = FMath::Min(MinimumRemoteDistance, Distance);
			if (Distance >= SharedCityQaMovementDistance)
			{
				++RemoteMovers;
			}
		}
		if (RemoteMovers >= SharedCityQaTargetClients - 1)
		{
			bSharedCityQaPassed = true;
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_SHARED_CITY_CAPACITY_PASS|clients=%d|remote_movers=%d|min_server_distance=%.1f|appearance_synced=true|starter_clothing_synced=true|names=true|pawn_collision=ignore"),
				SharedCityQaTargetClients,
				RemoteMovers,
				MinimumRemoteDistance);
			if (FParse::Param(FCommandLine::Get(), TEXT("SharedCityCapacityAutoExit")))
			{
				SharedCityQaExitAt = FPlatformTime::Seconds() + 5.0;
			}
		}
		return;
	}
	if (bSharedCityReconnectQa
		&& !bSharedCityReconnectLeaveObserved
		&& !SharedCityReconnectExpectedAppearance.bOwnerSubmitted)
	{
		for (const AOddsWellPlaceholderCharacter* Player : Players)
		{
			if (Player->GetSharedCityPlayerNumber() > 1 && Player->HasSubmittedSharedCityAppearance())
			{
				SharedCityReconnectExpectedAppearance = Player->GetSharedCityAppearance();
				SharedCityReconnectExpectedPlayerNumber = Player->GetSharedCityPlayerNumber();
				UE_LOG(
					LogOddsWellLocomotion,
					Display,
					TEXT("ODDSWELL_SHARED_CITY_RECONNECT_BASELINE|player=Player_%d|preset=%s|top=%s|bottom=%s|captured=true"),
					SharedCityReconnectExpectedPlayerNumber,
					*SharedCityReconnectExpectedAppearance.PresetId.ToString(),
					*SharedCityReconnectExpectedAppearance.TopItemId.ToString(),
					*SharedCityReconnectExpectedAppearance.BottomItemId.ToString());
				break;
			}
		}
	}
	if (bSharedCityReconnectQa && bSharedCityReconnectLeaveObserved)
	{
		for (const AOddsWellPlaceholderCharacter* Player : Players)
		{
			if (Player->GetSharedCityPlayerNumber() > SharedCityReconnectExpectedPlayerNumber
				&& MatchesSharedCityReconnectAppearance(SharedCityReconnectExpectedAppearance, Player->GetSharedCityAppearance()))
			{
				bSharedCityReconnectPassed = true;
				UE_LOG(
					LogOddsWellLocomotion,
					Display,
					TEXT("ODDSWELL_SHARED_CITY_RECONNECT_PASS|before=Player_%d|after=Player_%d|preset=%s|top=%s|bottom=%s|server_visible_restore=true|clients=%d"),
					SharedCityReconnectExpectedPlayerNumber,
					Player->GetSharedCityPlayerNumber(),
					*Player->GetSharedCityAppearance().PresetId.ToString(),
					*Player->GetSharedCityAppearance().TopItemId.ToString(),
					*Player->GetSharedCityAppearance().BottomItemId.ToString(),
					Players.Num());
				if (FParse::Param(FCommandLine::Get(), TEXT("SharedCityAutoExit")))
				{
					SharedCityQaExitAt = FPlatformTime::Seconds() + 5.0;
				}
				break;
			}
		}
	}
	for (const AOddsWellPlaceholderCharacter* Player : Players)
	{
		const FVector* Start = SharedCityQaStartLocations.Find(Player->GetSharedCityPlayerNumber());
		const float Distance = Start ? FVector::Dist2D(*Start, Player->GetActorLocation()) : 0.0f;
		if (!bSharedCityQaPassed
			&& Player->GetSharedCityPlayerNumber() > 1
			&& Distance >= SharedCityQaMovementDistance
			&& bAppearancesReady)
		{
			bSharedCityQaPassed = true;
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_SHARED_CITY_PASS|clients=%d|moving_player=Player_%d|server_distance=%.1f|replicated_movement=true|appearance_synced=true|starter_clothing_synced=true|names=true|pawn_collision=ignore"),
				Players.Num(),
				Player->GetSharedCityPlayerNumber(),
				Distance);
			if (!bSharedCityReconnectQa && FParse::Param(FCommandLine::Get(), TEXT("SharedCityAutoExit")))
			{
				SharedCityQaExitAt = FPlatformTime::Seconds() + 5.0;
			}
			break;
		}
	}
}

APawn* AOddsWellLocomotionGameMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&)
{
	FActorSpawnParameters Parameters;
	Parameters.Owner = NewPlayer;
	Parameters.ObjectFlags |= RF_Transient;
	Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	const int32 PlayerNumber = NextSharedCityPlayerNumber++;
	FVector SpawnLocation = SafeSpawnLocation + FVector(0.0, SharedCitySpawnSpacing * (PlayerNumber - 1), 0.0);
	if (GetNetMode() == NM_Standalone)
	{
		FOddsWellStudioHomeState Home;
		FString Error;
		if (LoadOwnedOddsWellStudio(UseOddsWellStudioHomeQaSlot(), Home, Error))
		{
			SpawnLocation = Home.SundaleReturnLocation;
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_RETURN_RESTORED|ownership=true|location=%s"), *SpawnLocation.ToCompactString());
		}
		if (UGameplayStatics::HasOption(OptionsString, TEXT("StadiumReturn")))
		{
			SpawnLocation = StadiumCityReturnLocation;
			Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_RETURN_RESTORED|location=%s|exact_xy=true"), *StadiumCityReturnLocation.ToCompactString());
		}
	}
	AOddsWellPlaceholderCharacter* Character = GetWorld()->SpawnActor<AOddsWellPlaceholderCharacter>(SpawnLocation, FRotator::ZeroRotator, Parameters);
	if (Character && GetNetMode() != NM_Standalone)
	{
		Character->AssignSharedCityPlayerNumber(PlayerNumber);
	}
	return Character;
}

AOddsWellStudioGameMode::AOddsWellStudioGameMode()
{
	DefaultPawnClass = AOddsWellPlaceholderCharacter::StaticClass();
}

void AOddsWellStudioGameMode::BeginPlay()
{
	Super::BeginPlay();
	FString CatalogError;
	if (!ValidateOddsWellHousingTiers(CatalogError))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_HOUSING_TIERS|result=FAIL|reason=%s"), *CatalogError);
		return;
	}
	TArray<FString> LockedTierIds;
	for (const FOddsWellHousingTier& Tier : GetOddsWellHousingTiers())
	{
		if (!Tier.bInteriorAvailable)
		{
			LockedTierIds.Add(Tier.Id.ToString());
		}
	}
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_HOUSING_TIERS|result=PASS|tiers=6|available=studio|locked=%s|larger_interiors=false|upgrade_ui=false"),
		*FString::Join(LockedTierIds, TEXT(",")));
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!Cube)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STUDIO_READY|result=FAIL|reason=missing_cube"));
		return;
	}
	FActorSpawnParameters Parameters;
	Parameters.ObjectFlags |= RF_Transient;
	for (const FStudioSurfaceSpec& Surface : GetEmptyStudioSurfaces())
	{
		AStaticMeshActor* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), FTransform(FRotator::ZeroRotator, Surface.Location, Surface.Scale), Parameters);
		if (Actor)
		{
			Actor->GetStaticMeshComponent()->SetStaticMesh(Cube);
			Actor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
			Actor->Tags.Add(StudioStructureTag);
		}
	}
	if (APointLight* Light = GetWorld()->SpawnActor<APointLight>(FVector(0.0, 0.0, 240.0), FRotator::ZeroRotator, Parameters))
	{
		Light->PointLightComponent->SetIntensity(5000.0f);
		Light->PointLightComponent->SetAttenuationRadius(1000.0f);
	}
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STUDIO_READY|result=PASS|private=true|visits=false|structure=%d|furniture=0|decorations=0|snap_points=0"), GetEmptyStudioSurfaces().Num());
}

APawn* AOddsWellStudioGameMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&)
{
	FActorSpawnParameters Parameters;
	Parameters.Owner = NewPlayer;
	Parameters.ObjectFlags |= RF_Transient;
	Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	return GetWorld()->SpawnActor<AOddsWellPlaceholderCharacter>(SafeSpawnLocation, FRotator::ZeroRotator, Parameters);
}

AOddsWellStadiumGameMode::AOddsWellStadiumGameMode()
{
	DefaultPawnClass = AOddsWellPlaceholderCharacter::StaticClass();
}

void AOddsWellStadiumGameMode::BeginPlay()
{
	Super::BeginPlay();
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!Cube)
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STADIUM_CONSTRUCTED|result=FAIL|reason=missing_cube"));
		return;
	}
	FActorSpawnParameters Parameters;
	Parameters.ObjectFlags |= RF_Transient;
	for (const FStadiumSurfaceSpec& Surface : GetStadiumSurfaces())
	{
		AStaticMeshActor* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), FTransform(FRotator::ZeroRotator, Surface.Location, Surface.Scale), Parameters);
		if (Actor)
		{
			Actor->GetStaticMeshComponent()->SetStaticMesh(Cube);
			Actor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
			Actor->Tags.Add(StadiumStructureTag);
			Actor->Tags.Add(Surface.Id);
		}
	}
	for (const FStadiumZoneSpec& Zone : GetStadiumZones())
	{
		ATextRenderActor* Label = GetWorld()->SpawnActor<ATextRenderActor>(Zone.Location, FRotator(0.0, 180.0, 0.0), Parameters);
		if (Label)
		{
			Label->Tags.Add(StadiumZoneTag);
			Label->Tags.Add(Zone.Id);
			Label->GetTextRender()->SetText(FText::FromString(Zone.Label));
			Label->GetTextRender()->SetHorizontalAlignment(EHTA_Center);
			Label->GetTextRender()->SetTextRenderColor(Zone.Id == TEXT("future_presentation") ? FColor::Yellow : FColor::White);
			Label->GetTextRender()->SetWorldSize(44.0f);
		}
	}
	if (APointLight* Light = GetWorld()->SpawnActor<APointLight>(FVector(0.0, 0.0, 500.0), FRotator::ZeroRotator, Parameters))
	{
		Light->PointLightComponent->SetIntensity(9000.0f);
		Light->PointLightComponent->SetAttenuationRadius(3500.0f);
	}
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_CONSTRUCTED|result=PASS|surfaces=%d|zones=%d|entry=true|concourse=true|court=true|public_viewing=true|future_marker=true|exit=true|unbranded=true|team_neutral=true"), GetStadiumSurfaces().Num(), GetStadiumZones().Num());
	const FTransform ReplayTransform(FRotator::ZeroRotator, StadiumReplayOrigin, FVector(StadiumReplayScale));
	const AReplayBenchmarkActor* Replay = GetWorld()->SpawnActor<AReplayBenchmarkActor>(AReplayBenchmarkActor::StaticClass(), ReplayTransform, Parameters);
	if (Replay)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_STADIUM_REPLAY_CONSUMER|spawned=true|source=Season1Game1|mode=authoritative_archived|resimulated=false|scale=%.2f"), StadiumReplayScale);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_STADIUM_REPLAY_CONSUMER|spawned=false"));
	}
}

APawn* AOddsWellStadiumGameMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&)
{
	FActorSpawnParameters Parameters;
	Parameters.Owner = NewPlayer;
	Parameters.ObjectFlags |= RF_Transient;
	Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	return GetWorld()->SpawnActor<AOddsWellPlaceholderCharacter>(StadiumInteriorSpawn, FRotator::ZeroRotator, Parameters);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellStadiumGrayboxTest,
	"OddsWell.Character.StadiumGraybox",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellStadiumGrayboxTest::RunTest(const FString& Parameters)
{
	const TArray<FStadiumSurfaceSpec>& Surfaces = GetStadiumSurfaces();
	const TArray<FStadiumZoneSpec>& Zones = GetStadiumZones();
	const TArray<FVector>& Waypoints = GetStadiumQaWaypoints();
	TestEqual(TEXT("Stadium uses the minimum eight primitive surfaces"), Surfaces.Num(), 8);
	TestEqual(TEXT("Stadium exposes exactly five required zones"), Zones.Num(), 5);
	TestEqual(TEXT("Stadium QA visits five zone points"), Waypoints.Num(), 5);
	TSet<FName> SurfaceIds;
	for (const FStadiumSurfaceSpec& Surface : Surfaces)
	{
		SurfaceIds.Add(Surface.Id);
		TestTrue(FString::Printf(TEXT("Surface %s has positive primitive scale"), *Surface.Id.ToString()), Surface.Scale.GetMin() > 0.0);
	}
	TestEqual(TEXT("Every stadium surface has a unique role"), SurfaceIds.Num(), Surfaces.Num());
	TestTrue(TEXT("Court floor is a distinct primitive"), SurfaceIds.Contains(TEXT("court_floor")));
	TestTrue(TEXT("Public viewing deck is a distinct primitive"), SurfaceIds.Contains(TEXT("viewing_deck")));
	TSet<FName> ZoneIds;
	for (const FStadiumZoneSpec& Zone : Zones)
	{
		ZoneIds.Add(Zone.Id);
		TestTrue(FString::Printf(TEXT("Zone %s remains inside the primitive room"), *Zone.Id.ToString()), FMath::Abs(Zone.Location.X) < 2000.0 && FMath::Abs(Zone.Location.Y) < 1200.0);
	}
	TestEqual(TEXT("Every required zone ID is unique"), ZoneIds.Num(), Zones.Num());
	TestTrue(TEXT("Entry/concourse is labeled"), ZoneIds.Contains(TEXT("entry_concourse")));
	TestTrue(TEXT("Court floor is labeled"), ZoneIds.Contains(TEXT("court_floor")));
	TestTrue(TEXT("Public viewing area is labeled"), ZoneIds.Contains(TEXT("public_viewing")));
	TestTrue(TEXT("Future presentation marker is labeled"), ZoneIds.Contains(TEXT("future_presentation")));
	TestTrue(TEXT("Exit is labeled"), ZoneIds.Contains(TEXT("exit")));
	TestTrue(TEXT("Stadium entrance reuses the existing Arena waypoint"), GetSundaleRouteWaypoints()[4].Equals(StadiumEntranceThreshold));
	TestTrue(TEXT("Sportsbook remains a separate city threshold"), FVector::Dist2D(GetSundaleRouteWaypoints()[5], StadiumEntranceThreshold) > StadiumEntryRadius * 2.0f);
	TestTrue(TEXT("Sportsbook interaction reuses its labeled route waypoint"), GetSundaleRouteWaypoints()[5].Equals(SportsbookInteractionLocation));
	TestTrue(TEXT("Sportsbook preview radius exceeds the player capsule"), SportsbookInteractionRadius > CapsuleRadius);
	TestTrue(TEXT("Sportsbook preview cannot overlap the Arena threshold"), FVector::Dist2D(SportsbookInteractionLocation, StadiumEntranceThreshold) > SportsbookInteractionRadius + StadiumEntryRadius);
	TestEqual(TEXT("Ticket booth uses the approved proximity prompt"), FString(TicketBoothOpenPrompt), FString(TEXT("Press E to open betting odds")));
	const TArray<FString>& MarketLabels = GetTicketBoothMarketLabels();
	TestEqual(TEXT("Ticket booth exposes four concise basketball market tabs"), MarketLabels.Num(), TicketBoothMarketPageCount);
	TestEqual(TEXT("Validated Match Winner offer owns the Game Lines tab"), MarketLabels[0], FString(TEXT("GAME LINES")));
	TestTrue(TEXT("Future score-margin category is visible"), MarketLabels.Contains(TEXT("MARGIN")));
	TestTrue(TEXT("Future overtime category is visible"), MarketLabels.Contains(TEXT("OVERTIME")));
	TestTrue(TEXT("Future athlete category is visible"), MarketLabels.Contains(TEXT("PLAYER PROPS")));
	TestTrue(TEXT("Stadium entry radius exceeds the player capsule"), StadiumEntryRadius > CapsuleRadius);
	TestTrue(TEXT("Archived replay consumer stays compact inside the stadium"), StadiumReplayScale > 0.0f && StadiumReplayScale <= 0.25f);
	TestTrue(TEXT("Archived replay consumer is anchored on the court"), StadiumReplayOrigin.Equals(FVector(350.0, 0.0, 0.0)));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalPendingReceiptHeldOpenTipoffTest,
	"OddsWell.League.CanonicalPendingReceiptHeldOpenMissingTipoff",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalPendingReceiptHeldOpenTipoffTest::RunTest(
	const FString& Parameters)
{
	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	TArray<uint8> BeforeBytes;
	const bool bLedgerExistedBefore =
		IFileManager::Get().FileExists(*QaLedgerPath);
	if (bLedgerExistedBefore)
	{
		TestTrue(
			TEXT("H26F held-open fixture reads existing ledger bytes"),
			FFileHelper::LoadFileToArray(BeforeBytes, *QaLedgerPath));
	}

	TUniquePtr<FOddsWellMatchWinnerOfferPreview> HeldOpenOffer =
		MakeUnique<FOddsWellMatchWinnerOfferPreview>();
	HeldOpenOffer->HomeTeam = TEXT("Harbor City Waves");
	HeldOpenOffer->AwayTeam = TEXT("Mesa Vista Sol");
	HeldOpenOffer->LockUnix = 2200001800;
	FOddsWellMatchWinnerSelectionPreview HomeSelection;
	HomeSelection.Team = HeldOpenOffer->HomeTeam;
	HomeSelection.DecimalOddsE4 = 17365;
	HeldOpenOffer->Selections.Add(HomeSelection);
	FOddsWellMatchWinnerSelectionPreview AwaySelection;
	AwaySelection.Team = HeldOpenOffer->AwayTeam;
	AwaySelection.DecimalOddsE4 = 23577;
	HeldOpenOffer->Selections.Add(AwaySelection);
	TUniquePtr<FOddsWellCanonicalPendingMatchWinnerReceipt> MissingReceipt;
	bool bMenuRemainsHeldOpen = true;

	ApplyTicketBoothEvidenceExpiry(
		HeldOpenOffer->LockUnix,
		EOddsWellCanonicalPendingReceiptResult::Missing,
		bMenuRemainsHeldOpen,
		HeldOpenOffer,
		MissingReceipt);

	TestTrue(
		TEXT("H26F no-request menu remains held open at tipoff"),
		bMenuRemainsHeldOpen);
	TestNull(
		TEXT("H26F held-open no-request tipoff clears all teams and prices"),
		HeldOpenOffer.Get());
	TestNull(
		TEXT("H26F held-open no-request tipoff exposes no pending receipt"),
		MissingReceipt.Get());

	TArray<uint8> AfterBytes;
	const bool bLedgerExistsAfter =
		IFileManager::Get().FileExists(*QaLedgerPath);
	TestEqual(
		TEXT("H26F held-open expiry creates no ledger or debit"),
		bLedgerExistsAfter,
		bLedgerExistedBefore);
	if (bLedgerExistedBefore && bLedgerExistsAfter)
	{
		TestTrue(
			TEXT("H26F held-open fixture rereads existing ledger bytes"),
			FFileHelper::LoadFileToArray(AfterBytes, *QaLedgerPath));
		TestTrue(
			TEXT("H26F held-open expiry leaves existing ledger bytes unchanged"),
			AfterBytes == BeforeBytes);
	}
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalSettledLossReceiptPresentationTest,
	"OddsWell.Locomotion.CanonicalSettledLossReceipt",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalSettledLossReceiptPresentationTest::RunTest(
	const FString& Parameters)
{
	FOddsWellCanonicalSettledLossReceipt Receipt;
	Receipt.Outcome = FName(TEXT("lost"));
	Receipt.SelectedTeam = TEXT("Harbor City Waves");
	Receipt.HomeTeam = TEXT("Harbor City Waves");
	Receipt.AwayTeam = TEXT("Mesa Vista Sol");
	Receipt.Winner = TEXT("Mesa Vista Sol");
	Receipt.Stake = 40;
	Receipt.HomeScore = 97;
	Receipt.AwayScore = 101;
	Receipt.Returned = 0;
	Receipt.Net = -40;
	Receipt.LedgerEntryCount = 2;
	Receipt.CurrentBalance = 60;
	const FString Text = BuildCanonicalSettledLossReceiptText(Receipt);
	TArray<FString> Lines;
	Text.ParseIntoArrayLines(Lines, false);
	TestEqual(TEXT("H26P receipt contains nine concise lines"), Lines.Num(), 9);
	TestEqual(
		TEXT("H26P receipt headline is an exact settled loss"),
		Lines[0],
		FString(TEXT("BET SETTLED \u2014 LOSS")));
	TestTrue(
		TEXT("H26P receipt shows only approved result values"),
		Text.Contains(TEXT("Harbor City Waves selected"))
			&& Text.Contains(TEXT("Stake 40 Odds Bucks"))
			&& Text.Contains(TEXT("Final Harbor 97\u2013101 Mesa"))
			&& Text.Contains(TEXT("Winner Mesa Vista Sol"))
			&& Text.Contains(TEXT("Returned 0"))
			&& Text.Contains(TEXT("Net -40"))
			&& Text.Contains(TEXT("Balance 60")));
	Receipt.Outcome = FName(TEXT("won"));
	Receipt.SelectedTeam = TEXT("Mesa Vista Sol");
	Receipt.HomeScore = 79;
	Receipt.AwayScore = 113;
	Receipt.Returned = 94;
	Receipt.Net = 54;
	Receipt.LedgerEntryCount = 3;
	Receipt.CurrentBalance = 154;
	const FString WinText = BuildCanonicalSettledLossReceiptText(Receipt);
	TestTrue(
		TEXT("H26AL receipt reuses the same surface for the exact current win"),
		WinText.Contains(TEXT("BET SETTLED \u2014 WIN"))
			&& WinText.Contains(TEXT("Mesa Vista Sol selected"))
			&& WinText.Contains(TEXT("Final Harbor 79\u2013113 Mesa"))
			&& WinText.Contains(TEXT("Returned 94"))
			&& WinText.Contains(TEXT("Net +54"))
			&& WinText.Contains(TEXT("Balance 154")));
	const int32 FirstClose = Text.Find(TEXT("CLOSE"));
	TestTrue(
		TEXT("H26P receipt contains exactly one close instruction"),
		FirstClose != INDEX_NONE
			&& FirstClose
				== Text.Find(
					TEXT("CLOSE"),
					ESearchCase::CaseSensitive,
					ESearchDir::FromEnd));
	const FString Lower = Text.ToLower();
	TestFalse(
		TEXT("H26P receipt exposes no command IDs, hashes, seeds, or athlete data"),
		Lower.Contains(TEXT("command"))
			|| Lower.Contains(TEXT("hash"))
			|| Lower.Contains(TEXT("seed"))
			|| Lower.Contains(TEXT("athlete"))
			|| Lower.Contains(TEXT("offer"))
			|| Lower.Contains(TEXT("request")));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalSettledLossHandoffCueTest,
	"OddsWell.Locomotion.CanonicalSettledLossHandoffCue",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalSettledLossHandoffCueTest::RunTest(
	const FString& Parameters)
{
	const FString MapName(TEXT("UEDPIE_0_SundaleGraybox"));
	FString Cue;
	const auto BuildsCue = [&](const FVector& Location, const float Yaw)
	{
		return BuildSettledLossHandoffCue(
			true,
			MapName,
			Location,
			Yaw,
			false,
			false,
			false,
			Cue);
	};

	TestTrue(TEXT("H26AH.1 hands a valid H26P receipt to the city cue"), BuildsCue(SafeSpawnLocation, 0.0f));
	TestEqual(
		TEXT("H26AH.1 start cue derives right and 180 meters"),
		Cue,
		FString(TEXT("SETTLED BET READY \u2014 TICKET BOOTH: RIGHT \u2014 180 m")));
	TestTrue(TEXT("H26AH.1 derives ahead"), BuildsCue(SportsbookInteractionLocation - FVector(10000.0f, 0.0f, 0.0f), 0.0f));
	TestTrue(TEXT("H26AH.1 ahead cue keeps 100 meter distance"), Cue.Contains(TEXT("AHEAD \u2014 100 m")));
	TestTrue(TEXT("H26AH.1 derives behind"), BuildsCue(SportsbookInteractionLocation + FVector(10000.0f, 0.0f, 0.0f), 0.0f));
	TestTrue(TEXT("H26AH.1 behind cue keeps 100 meter distance"), Cue.Contains(TEXT("BEHIND \u2014 100 m")));
	TestTrue(TEXT("H26AH.1 derives right"), BuildsCue(SportsbookInteractionLocation - FVector(0.0f, 10000.0f, 0.0f), 0.0f));
	TestTrue(TEXT("H26AH.1 right cue keeps 100 meter distance"), Cue.Contains(TEXT("RIGHT \u2014 100 m")));
	TestTrue(TEXT("H26AH.1 derives left"), BuildsCue(SportsbookInteractionLocation + FVector(0.0f, 10000.0f, 0.0f), 0.0f));
	TestTrue(TEXT("H26AH.1 left cue keeps 100 meter distance"), Cue.Contains(TEXT("LEFT \u2014 100 m")));

	TestFalse(TEXT("H26AH.1 invalid receipt exposes no cue"), BuildSettledLossHandoffCue(false, MapName, SafeSpawnLocation, 0.0f, false, false, false, Cue));
	TestTrue(TEXT("H26AH.1 invalid receipt clears handoff text"), Cue.IsEmpty());
	TestFalse(TEXT("H26AH.1 wrong map exposes no cue"), BuildSettledLossHandoffCue(true, TEXT("Bootstrap"), SafeSpawnLocation, 0.0f, false, false, false, Cue));
	TestFalse(TEXT("H26AH.1 hides while receipt menu is open"), BuildSettledLossHandoffCue(true, MapName, SafeSpawnLocation, 0.0f, true, false, false, Cue));
	TestFalse(TEXT("H26AH.1 hides inside Studio"), BuildSettledLossHandoffCue(true, MapName, SafeSpawnLocation, 0.0f, false, true, false, Cue));
	TestFalse(TEXT("H26AH.1 hides inside stadium"), BuildSettledLossHandoffCue(true, MapName, SafeSpawnLocation, 0.0f, false, false, true, Cue));
	TestFalse(
		TEXT("H26AH.1 yields to the existing booth-radius prompt"),
		BuildSettledLossHandoffCue(
			true,
			MapName,
			SportsbookInteractionLocation + FVector(SportsbookInteractionRadius, 0.0f, 0.0f),
			0.0f,
			false,
			false,
			false,
			Cue));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalBetSlipReviewTest,
	"OddsWell.Locomotion.CanonicalBetSlipReview",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalBetSlipReviewTest::RunTest(
	const FString& Parameters)
{
	FOddsWellMatchWinnerOfferPreview Offer;
	Offer.HomeTeam = TEXT("Harbor City Waves");
	Offer.AwayTeam = TEXT("Mesa Vista Sol");
	Offer.MinimumStake = 10;
	Offer.MaximumStake = 100;
	Offer.StakeIncrement = 10;
	FOddsWellMatchWinnerSelectionPreview Harbor;
	Harbor.Team = Offer.HomeTeam;
	Harbor.WinProbabilityE8 = 57586693;
	Harbor.DecimalOddsE4 = 17365;
	Offer.Selections.Add(Harbor);
	FOddsWellMatchWinnerSelectionPreview Mesa;
	Mesa.Team = Offer.AwayTeam;
	Mesa.WinProbabilityE8 = 42413307;
	Mesa.DecimalOddsE4 = 23577;
	Offer.Selections.Add(Mesa);
	TestTrue(TEXT("H26Q accepts only the exact two-team stake contract"), IsCanonicalBetSlipOfferUsable(Offer));

	const int64 ExpectedGrossReturns[2][10] = {
		{17, 34, 52, 69, 86, 104, 121, 138, 156, 173},
		{23, 47, 70, 94, 117, 141, 165, 188, 212, 235}};
	for (int32 SelectionIndex = 0; SelectionIndex < 2; ++SelectionIndex)
	{
		for (int32 StakeIndex = 0; StakeIndex < 10; ++StakeIndex)
		{
			const int64 Stake = 10 + StakeIndex * 10;
			TestEqual(
				FString::Printf(
					TEXT("H26Q %s stake %lld has exact integer-formula gross return"),
					*Offer.Selections[SelectionIndex].Team,
					Stake),
				CalculateCanonicalBetSlipGrossReturn(
					Stake,
					Offer.Selections[SelectionIndex].WinProbabilityE8),
				ExpectedGrossReturns[SelectionIndex][StakeIndex]);
		}
	}

	const FString ReviewText = BuildCanonicalBetSlipReviewText(Offer, 1, 40, 100);
	TestTrue(
		TEXT("H26Q selected slip exposes only the approved review values"),
		ReviewText.Contains(TEXT("Mesa Vista Sol"))
			&& ReviewText.Contains(TEXT("DECIMAL ODDS 2.3577"))
			&& ReviewText.Contains(TEXT("STAKE 40 Odds Bucks"))
			&& ReviewText.Contains(TEXT("POTENTIAL GROSS RETURN 94 Odds Bucks"))
			&& ReviewText.Contains(TEXT("CURRENT BALANCE 100 Odds Bucks"))
			&& ReviewText.Contains(TEXT("LOCKS AT GAME START"))
			&& ReviewText.Contains(TEXT("REVIEW ONLY \u2014 WAGER NOT PLACED")));
	TestTrue(
		TEXT("H26Q slip labels mouse, keyboard, and controller routes"),
		ReviewText.Contains(TEXT("MOUSE:"))
			&& ReviewText.Contains(TEXT("KEYBOARD:"))
			&& ReviewText.Contains(TEXT("CONTROLLER:")));
	const FString LowerReviewText = ReviewText.ToLower();
	TestFalse(
		TEXT("H26Q review exposes no confirm, submit, request, debit, IDs, hashes, or seeds"),
		LowerReviewText.Contains(TEXT("confirm"))
			|| LowerReviewText.Contains(TEXT("submit"))
			|| LowerReviewText.Contains(TEXT("request"))
			|| LowerReviewText.Contains(TEXT("debit"))
			|| LowerReviewText.Contains(TEXT("offer_id"))
			|| LowerReviewText.Contains(TEXT("hash"))
			|| LowerReviewText.Contains(TEXT("seed")));
	TestTrue(
		TEXT("H26Q mouse routes have stable visible-focus hitboxes"),
		TicketBoothHomeTeamHitBox == TEXT("TicketBoothTeam0")
			&& TicketBoothAwayTeamHitBox == TEXT("TicketBoothTeam1")
			&& TicketBoothStakeDecreaseHitBox == TEXT("TicketBoothStakeDecrease")
			&& TicketBoothStakeIncreaseHitBox == TEXT("TicketBoothStakeIncrease"));
	TestTrue(
		TEXT("H26Q controller routes are D-pad gamepad keys"),
		KeyControllerTeamPrevious.IsGamepadKey()
			&& KeyControllerTeamNext.IsGamepadKey()
			&& KeyControllerStakeDecrease.IsGamepadKey()
			&& KeyControllerStakeIncrease.IsGamepadKey());
	TestTrue(
		TEXT("H26Q keyboard team and stake routes remain non-gamepad keys"),
		!KeyLeaguePrevious.IsGamepadKey()
			&& !KeyLeagueNext.IsGamepadKey()
			&& !KeyStakeDecrease.IsGamepadKey()
			&& !KeyStakeIncrease.IsGamepadKey());
	TestTrue(
		TEXT("H26Q pending and settled receipts retain precedence over review"),
		ShouldShowCanonicalBetSlipReview(true, false, false)
			&& !ShouldShowCanonicalBetSlipReview(true, true, false)
			&& !ShouldShowCanonicalBetSlipReview(true, false, true)
			&& !ShouldShowCanonicalBetSlipReview(true, true, true)
			&& !ShouldShowCanonicalBetSlipReview(false, false, false));
	Offer.StakeIncrement = 0;
	TestFalse(TEXT("H26Q rejects malformed H26A-C offer state"), IsCanonicalBetSlipOfferUsable(Offer));
	TestEqual(
		TEXT("H26Q malformed offer reveals no partial values"),
		BuildCanonicalBetSlipReviewText(Offer, 1, 40, 100),
		FString(TEXT("BET SLIP UNAVAILABLE")));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalFortyPlacementTest,
	"OddsWell.Locomotion.CanonicalFortyPlacement",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalFortyPlacementTest::RunTest(
	const FString& Parameters)
{
	FOddsWellMatchWinnerOfferPreview Offer;
	Offer.HomeTeam = TEXT("Harbor City Waves");
	Offer.AwayTeam = TEXT("Mesa Vista Sol");
	Offer.MinimumStake = 10;
	Offer.MaximumStake = 100;
	Offer.StakeIncrement = 10;
	FOddsWellMatchWinnerSelectionPreview& Harbor =
		Offer.Selections.AddDefaulted_GetRef();
	Harbor.Team = Offer.HomeTeam;
	Harbor.WinProbabilityE8 = 57586693;
	Harbor.DecimalOddsE4 = 17365;
	FOddsWellMatchWinnerSelectionPreview& Mesa =
		Offer.Selections.AddDefaulted_GetRef();
	Mesa.Team = Offer.AwayTeam;
	Mesa.WinProbabilityE8 = 42413307;
	Mesa.DecimalOddsE4 = 23577;

	TestTrue(
		TEXT("H26AM Harbor at 40 with sufficient balance remains eligible"),
		IsCanonicalFortyPlacementEligible(Offer, 0, 40, 100));
	TestFalse(
		TEXT("H26R no selection is unavailable"),
		IsCanonicalFortyPlacementEligible(
			Offer,
			INDEX_NONE,
			40,
			100));
	TestTrue(
		TEXT("H26AM Mesa at 40 with sufficient balance is eligible"),
		IsCanonicalFortyPlacementEligible(Offer, 1, 40, 100));
	for (int64 Stake = 10; Stake <= 100; Stake += 10)
	{
		if (Stake != 40)
		{
			TestFalse(
				FString::Printf(
					TEXT("H26R Harbor stake %lld is unavailable"),
					Stake),
				IsCanonicalFortyPlacementEligible(
					Offer,
					0,
					Stake,
					100));
		}
	}
	TestFalse(
		TEXT("H26R insufficient balance is unavailable"),
		IsCanonicalFortyPlacementEligible(Offer, 0, 40, 39));

	bool bArmed = false;
	TestFalse(
		TEXT("H26R first confirmation does not submit"),
		AdvanceCanonicalFortyConfirmation(true, bArmed));
	TestTrue(TEXT("H26R first confirmation visibly arms"), bArmed);
	TestTrue(
		TEXT("H26R second confirmation submits"),
		AdvanceCanonicalFortyConfirmation(true, bArmed));
	TestFalse(TEXT("H26R submission clears the arm"), bArmed);
	bArmed = true;
	TestFalse(
		TEXT("H26R an ineligible change cannot submit"),
		AdvanceCanonicalFortyConfirmation(false, bArmed));
	TestFalse(TEXT("H26R an ineligible change disarms"), bArmed);
	TestTrue(
		TEXT("H26R mouse and keyboard/controller confirm routes are present"),
		TicketBoothConfirmHitBox == TEXT("TicketBoothConfirm")
			&& !KeyConfirm.IsGamepadKey()
			&& KeyControllerJump.IsGamepadKey());

	Offer.StakeIncrement = 0;
	TestFalse(
		TEXT("H26R malformed H26A-C evidence is unavailable"),
		IsCanonicalFortyPlacementEligible(Offer, 0, 40, 100));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalAutomaticTipoffLockTest,
	"OddsWell.Locomotion.CanonicalAutomaticTipoffLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalAutomaticTipoffLockTest::RunTest(
	const FString& Parameters)
{
	constexpr int64 CreatedUnix = 2200000000;
	constexpr int64 TipoffUnix = CreatedUnix + 1800;
	TestTrue(
		TEXT("H26S a restored pending request schedules before tipoff"),
		ShouldScheduleCanonicalMatchWinnerTipoffLock(
			false,
			CreatedUnix + 100,
			TipoffUnix));
	TestFalse(
		TEXT("H26S an existing timer prevents a duplicate timer"),
		ShouldScheduleCanonicalMatchWinnerTipoffLock(
			true,
			CreatedUnix + 100,
			TipoffUnix));
	TestFalse(
		TEXT("H26S exact tipoff never schedules a catch-up timer"),
		ShouldScheduleCanonicalMatchWinnerTipoffLock(
			false,
			TipoffUnix,
			TipoffUnix));
	TestFalse(
		TEXT("H26S post-tipoff restore never schedules a catch-up timer"),
		ShouldScheduleCanonicalMatchWinnerTipoffLock(
			false,
			TipoffUnix + 1,
			TipoffUnix));
	TestFalse(
		TEXT("H26S an early callback cannot invoke H26G"),
		IsExactCanonicalMatchWinnerTipoff(TipoffUnix - 1, TipoffUnix));
	TestTrue(
		TEXT("H26S only exact H26A tipoff can invoke H26G"),
		IsExactCanonicalMatchWinnerTipoff(TipoffUnix, TipoffUnix));
	TestFalse(
		TEXT("H26S a late callback cannot backdate H26G"),
		IsExactCanonicalMatchWinnerTipoff(TipoffUnix + 1, TipoffUnix));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalAutomaticResultLinkTest,
	"OddsWell.Locomotion.CanonicalAutomaticResultLink",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalAutomaticResultLinkTest::RunTest(
	const FString& Parameters)
{
	TestFalse(
		TEXT("H26AE missing private result evidence is a no-op"),
		ShouldAttemptCanonicalMatchWinnerResultLink(0));
	TestTrue(
		TEXT("H26AE one private result delegates to the strict H26L transition"),
		ShouldAttemptCanonicalMatchWinnerResultLink(1));
	TestTrue(
		TEXT("H26AE conflicting private results delegate to H26L rejection"),
		ShouldAttemptCanonicalMatchWinnerResultLink(2));

	FOddsWellMatchWinnerResultLinkRecord Linked;
	Linked.ResultCommandId = TEXT("canonical:h26l:match_winner:result:record");
	Linked.RequestCommandId = TEXT("canonical:h26e:match_winner:request:offer");
	Linked.LockCommandId = TEXT("canonical:h26g:match_winner:lock:offer");
	Linked.ResultSchema = TEXT("oddswell-private-canonical-game-result-v1");
	Linked.ResultVersion = TEXT("oddswell-private-game-result-recorder-v1");
	Linked.SeasonNumber = 1;
	Linked.GameNumber = 1;
	Linked.HomeTeam = TEXT("Harbor City Waves");
	Linked.AwayTeam = TEXT("Mesa Vista Sol");
	Linked.HomeScore = 79;
	Linked.AwayScore = 113;
	Linked.Winner = Linked.AwayTeam;
	Linked.ReplaySealSha256 = TEXT("replay");
	TestTrue(
		TEXT("H26AE accepts an exact durable reload"),
		IsSameCanonicalMatchWinnerResultLink(Linked, Linked));
	FOddsWellMatchWinnerResultLinkRecord Conflicting = Linked;
	Conflicting.AwayScore += 1;
	TestFalse(
		TEXT("H26AE rejects a conflicting durable reload"),
		IsSameCanonicalMatchWinnerResultLink(Linked, Conflicting));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalAutomaticLossDecisionTest,
	"OddsWell.Locomotion.CanonicalAutomaticLossDecision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalAutomaticLossDecisionTest::RunTest(
	const FString& Parameters)
{
	FOddsWellMatchWinnerResultLinkRecord Result;
	Result.ResultCommandId =
		TEXT("canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Result.RequestCommandId =
		TEXT("canonical:h26e:match_winner:request:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Result.LockCommandId =
		TEXT("canonical:h26g:match_winner:lock:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Result.ResultSchema =
		TEXT("oddswell-private-canonical-game-result-v1");
	Result.ResultVersion =
		TEXT("oddswell-private-game-result-recorder-v1");
	Result.SeasonNumber = 1;
	Result.GameNumber = 1;
	Result.HomeTeam = TEXT("Harbor City Waves");
	Result.AwayTeam = TEXT("Mesa Vista Sol");
	Result.HomeScore = 79;
	Result.AwayScore = 113;
	Result.Winner = Result.AwayTeam;
	Result.ReplaySealSha256 =
		TEXT("35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db");
	TestTrue(
		TEXT("H26AF durable reload requires the exact current H26L result"),
		IsExactCurrentCanonicalMatchWinnerResultLink(Result));
	Result.HomeScore += 1;
	TestFalse(
		TEXT("H26AF rejects a changed current result"),
		IsExactCurrentCanonicalMatchWinnerResultLink(Result));

	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	Decision.DecisionCommandId =
		TEXT("canonical:h26m:match_winner:decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Decision.RequestCommandId =
		TEXT("canonical:h26e:match_winner:request:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Decision.LockCommandId =
		TEXT("canonical:h26g:match_winner:lock:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Decision.ResultCommandId =
		TEXT("canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Decision.DecisionSchema =
		TEXT("oddswell-match-winner-settlement-decision-v1");
	Decision.DecisionVersion =
		TEXT("match-winner-settlement-decision-v1");
	Decision.OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Decision.OfferVersion = TEXT("basketball-match-winner-odds-v1");
	Decision.SelectedTeam = TEXT("Harbor City Waves");
	Decision.AuthoritativeWinner = TEXT("Mesa Vista Sol");
	Decision.Stake = 40;
	Decision.Outcome = FName(TEXT("lost"));
	Decision.GrossReturnDue = 0;
	Decision.Status = FName(TEXT("decided_pending_apply"));
	TestTrue(
		TEXT("H26AF accepts only the exact current loss decision"),
		IsExactCurrentCanonicalMatchWinnerLossDecision(Decision));
	Decision.Status = FName(TEXT("settled_lost"));
	TestFalse(
		TEXT("H26AF rejects later decision state"),
		IsExactCurrentCanonicalMatchWinnerLossDecision(Decision));

	TestTrue(
		TEXT("H26AF cold duplicate follows only exact H26L downstream rejection"),
		CanResumeCanonicalLossDecisionAfterResultLinkRejection(
			TEXT("Canonical Match Winner result linking requires exact schema-12 H26E/H26G evidence and no downstream state.")));
	TestTrue(
		TEXT("H26AF cold duplicate can pass the parameterless H26L prerequisite boundary"),
		CanResumeCanonicalLossDecisionAfterResultLinkRejection(
			TEXT("Canonical Match Winner result prerequisites failed exact H26A/B/C/E/G validation.")));
	TestFalse(
		TEXT("H26AF malformed private evidence cannot use cold duplicate resume"),
		CanResumeCanonicalLossDecisionAfterResultLinkRejection(
			TEXT("The private H26K result conflicts with exact H26H/H26J evidence.")));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalAutomaticMesaWinDecisionTest,
	"OddsWell.Locomotion.CanonicalAutomaticMesaWinDecision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalAutomaticMesaWinDecisionTest::RunTest(
	const FString& Parameters)
{
	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	Decision.DecisionCommandId =
		TEXT("canonical:h26an:match_winner:win-decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Decision.RequestCommandId =
		TEXT("canonical:h26e:match_winner:request:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Decision.LockCommandId =
		TEXT("canonical:h26g:match_winner:lock:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Decision.ResultCommandId =
		TEXT("canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Decision.DecisionSchema =
		TEXT("oddswell-match-winner-settlement-decision-v1");
	Decision.DecisionVersion =
		TEXT("match-winner-settlement-decision-v1");
	Decision.OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Decision.OfferVersion = TEXT("basketball-match-winner-odds-v1");
	Decision.SelectedTeam = TEXT("Mesa Vista Sol");
	Decision.AuthoritativeWinner = TEXT("Mesa Vista Sol");
	Decision.Stake = 40;
	Decision.Outcome = FName(TEXT("won"));
	Decision.GrossReturnDue = 94;
	Decision.SelectedWinProbabilityE8 = 42413307;
	Decision.PayoutFormula =
		TEXT("floor(stake*100000000/win_probability_e8)");
	Decision.Status = FName(TEXT("decided_pending_apply"));
	TestTrue(
		TEXT("H26AN accepts only the exact current Mesa win decision"),
		IsExactCurrentCanonicalMatchWinnerMesaWinDecision(Decision));

	FOddsWellMatchWinnerSettlementDecisionRecord Changed = Decision;
	Changed.SelectedTeam = TEXT("Harbor City Waves");
	TestFalse(
		TEXT("H26AN rejects the retained Harbor selection as Mesa evidence"),
		IsExactCurrentCanonicalMatchWinnerMesaWinDecision(Changed));
	Changed = Decision;
	Changed.GrossReturnDue++;
	TestFalse(
		TEXT("H26AN rejects a changed return"),
		IsExactCurrentCanonicalMatchWinnerMesaWinDecision(Changed));
	Changed = Decision;
	Changed.Status = FName(TEXT("settled_won"));
	TestFalse(
		TEXT("H26AN rejects later finalization state"),
		IsExactCurrentCanonicalMatchWinnerMesaWinDecision(Changed));
	Changed = Decision;
	Changed.ResultCommandId += TEXT(":foreign");
	TestFalse(
		TEXT("H26AN rejects foreign result identity"),
		IsExactCurrentCanonicalMatchWinnerMesaWinDecision(Changed));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalAutomaticLossFinalizationTest,
	"OddsWell.Locomotion.CanonicalAutomaticLossFinalization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalAutomaticLossFinalizationTest::RunTest(
	const FString& Parameters)
{
	FOddsWellMatchWinnerLossFinalizationRecord Finalization;
	Finalization.FinalizationCommandId =
		TEXT("canonical:h26n:match_winner:finalization:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Finalization.DecisionCommandId =
		TEXT("canonical:h26m:match_winner:decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Finalization.RequestCommandId =
		TEXT("canonical:h26e:match_winner:request:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Finalization.LockCommandId =
		TEXT("canonical:h26g:match_winner:lock:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Finalization.ResultCommandId =
		TEXT("canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	Finalization.FinalizationSchema =
		TEXT("oddswell-match-winner-loss-finalization-v1");
	Finalization.FinalizationVersion =
		TEXT("match-winner-loss-finalization-v1");
	Finalization.OfferId =
		TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d");
	Finalization.OfferVersion = TEXT("basketball-match-winner-odds-v1");
	Finalization.SelectedTeam = TEXT("Harbor City Waves");
	Finalization.AuthoritativeWinner = TEXT("Mesa Vista Sol");
	Finalization.Stake = 40;
	Finalization.Outcome = FName(TEXT("lost"));
	Finalization.GrossReturnApplied = 0;
	Finalization.Status = FName(TEXT("settled_lost"));
	Finalization.ObservedFinalBalance = 60;
	Finalization.ObservedLedgerEntryCount = 2;
	TestTrue(
		TEXT("H26AG accepts only the exact current loss finalization"),
		IsExactCurrentCanonicalMatchWinnerLossFinalization(
			Finalization));
	Finalization.GrossReturnApplied = 1;
	TestFalse(
		TEXT("H26AG rejects a nonzero loss application"),
		IsExactCurrentCanonicalMatchWinnerLossFinalization(
			Finalization));

	TestTrue(
		TEXT("H26AG cold duplicate follows only exact H26M later-state rejection"),
		CanResumeCanonicalLossFinalizationAfterDecisionRejection(
			TEXT("Canonical Match Winner loss decision requires exact schema-12 evidence and no later state.")));
	TestFalse(
		TEXT("H26AG nonloss evidence cannot use the cold duplicate path"),
		CanResumeCanonicalLossFinalizationAfterDecisionRejection(
			TEXT("Canonical Match Winner loss decision requires the exact current H26E/H26G/H26L chain.")));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellLocomotionDefaultsTest,
	"OddsWell.Character.LocomotionDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellLocomotionDefaultsTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("Walk speed is positive"), WalkSpeed > 0.0f);
	TestTrue(TEXT("Held run is faster than walk"), RunSpeed > WalkSpeed);
	TestTrue(TEXT("Native jump has positive velocity"), JumpVelocity > 0.0f);
	TestTrue(TEXT("Trailing camera has positive distance"), CameraDistance > 0.0f);
	TestTrue(TEXT("Spring arm collision remains enabled"), UseCameraCollision);
	TestTrue(TEXT("Safe spawn starts above the capsule"), SafeSpawnLocation.Z > CapsuleHalfHeight && CapsuleRadius > 0.0f);
	TestTrue(TEXT("Camera pitch is bounded"), CameraPitchMin > -90.0f && CameraPitchMax < 90.0f && CameraPitchMin < CameraPitchMax);
	TestTrue(TEXT("Two-player proof uses separated spawn points"), SharedCitySpawnSpacing > CapsuleRadius * 2.0f);
	TestTrue(TEXT("Shared-city QA requires measurable movement"), SharedCityQaMovementDistance > SharedCitySpawnSpacing);
	TestEqual(TEXT("Local capacity ladder starts at two clients"), SharedCityCapacityMinClients, 2);
	TestEqual(TEXT("Local capacity ladder stops at four clients"), SharedCityCapacityMaxClients, 4);
	TestEqual(TEXT("Empty Studio contains only six structural surfaces"), GetEmptyStudioSurfaces().Num(), 6);
	TestTrue(TEXT("Studio entry is local to the city start"), StudioEntryRadius > CapsuleRadius);
	TestTrue(TEXT("Studio QA proves walkable floor space"), StudioQaWalkDistance > CapsuleRadius * 2.0f);
	TestTrue(TEXT("Players pass through one another"), SharedCityPlayerCollision == ECR_Ignore);
	FOddsWellSharedCityAppearance ReconnectBefore;
	ReconnectBefore.PresetId = TEXT("feminine_tone_4");
	ReconnectBefore.TopItemId = TEXT("starter_offwhite_top");
	ReconnectBefore.BottomItemId = TEXT("starter_offwhite_bottom");
	ReconnectBefore.bOwnerSubmitted = true;
	FOddsWellSharedCityAppearance ReconnectAfter = ReconnectBefore;
	TestTrue(TEXT("Reconnect accepts the same submitted visible state"), MatchesSharedCityReconnectAppearance(ReconnectBefore, ReconnectAfter));
	ReconnectAfter.PresetId = TEXT("masculine_tone_1");
	TestFalse(TEXT("Reconnect rejects a changed preset"), MatchesSharedCityReconnectAppearance(ReconnectBefore, ReconnectAfter));
	ReconnectAfter = ReconnectBefore;
	ReconnectAfter.bOwnerSubmitted = false;
	TestFalse(TEXT("Reconnect rejects an unsubmitted fallback"), MatchesSharedCityReconnectAppearance(ReconnectBefore, ReconnectAfter));

	const TArray<FKey> KeyboardMoveKeys = {KeyForward, KeyBackward, KeyLeft, KeyRight};
	const TArray<FKey> MouseLookKeys = {KeyMouseYaw, KeyMousePitch};
	const TArray<FKey> ControllerMoveLookKeys = {KeyControllerMoveX, KeyControllerMoveY, KeyControllerLookX, KeyControllerLookY};
	TestEqual(TEXT("Keyboard movement polling routes are complete"), KeyboardMoveKeys.Num(), 4);
	TestEqual(TEXT("Mouse look axis routes are complete"), MouseLookKeys.Num(), 2);
	TestEqual(TEXT("Controller movement/look routes are complete"), ControllerMoveLookKeys.Num(), 4);
	for (const FKey& Key : KeyboardMoveKeys)
	{
		TestFalse(FString::Printf(TEXT("Digital keyboard key %s is not bound as an axis"), *Key.ToString()), Key.IsAxis1D());
	}
	for (const FKey& Key : MouseLookKeys)
	{
		TestTrue(FString::Printf(TEXT("Mouse look key %s is a one-dimensional axis"), *Key.ToString()), Key.IsAxis1D());
	}
	for (const FKey& Key : ControllerMoveLookKeys)
	{
		TestTrue(FString::Printf(TEXT("Controller axis %s is a gamepad route"), *Key.ToString()), Key.IsGamepadKey());
		TestTrue(FString::Printf(TEXT("Controller axis %s is one-dimensional"), *Key.ToString()), Key.IsAxis1D());
	}
	TestFalse(TEXT("Keyboard run route is not a gamepad key"), KeyRun.IsGamepadKey());
	TestFalse(TEXT("Keyboard jump route is not a gamepad key"), KeyJump.IsGamepadKey());
	TestTrue(TEXT("Controller run route is present"), KeyControllerRun.IsGamepadKey());
	TestTrue(TEXT("Controller jump route is present"), KeyControllerJump.IsGamepadKey());
	TestTrue(TEXT("Controller market navigation routes are present"), KeyControllerMarketPrevious.IsGamepadKey() && KeyControllerMarketNext.IsGamepadKey());
	TestTrue(TEXT("Controller ticket booth close route is present"), KeyControllerMenuClose.IsGamepadKey());

	TestFalse(TEXT("Crouch is not supported"), AllowCrouch);
	TestFalse(TEXT("Flight is not supported"), AllowFlight);
	TestFalse(TEXT("Swimming is not supported"), AllowSwimming);
	const TArray<FVector>& SundaleWaypoints = GetSundaleRouteWaypoints();
	TestEqual(TEXT("Sundale route keeps the minimal eleven waypoints"), SundaleWaypoints.Num(), 11);
	float SundaleDistance = 0.0f;
	FVector PreviousPoint = FVector::ZeroVector;
	for (const FVector& Point : SundaleWaypoints)
	{
		SundaleDistance += FVector::Dist2D(PreviousPoint, Point);
		PreviousPoint = Point;
	}
	TestTrue(TEXT("Sundale route remains exactly 800 meters"), FMath::IsNearlyEqual(SundaleDistance, SundaleRouteDistance));
	TestEqual(TEXT("Sundale route labels match waypoints"), GetSundaleRouteWaypointLabels().Num(), SundaleWaypoints.Num());
	TestTrue(TEXT("Approved Job interaction reuses the first route waypoint"), JobInteractionLocation.Equals(SundaleWaypoints[0]));
	TestEqual(TEXT("First route waypoint remains labeled Job"), GetSundaleRouteWaypointLabels()[0], FString(TEXT("Job")));
	TestTrue(TEXT("Job interaction radius exceeds the player capsule"), JobInteractionRadius > CapsuleRadius);
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellStarterOutfitTest,
	"OddsWell.Character.StarterOutfit",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellStarterOutfitTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("Character preset catalog remains valid"), ValidateOddsWellCharacterPresets(Error));
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	TestEqual(TEXT("All eight presets remain available"), Presets.Num(), 8);
	if (Presets.Num() != 8)
	{
		return false;
	}
	for (const FOddsWellCharacterPreset& Preset : Presets)
	{
		TestEqual(TEXT("Every preset has exactly two equipment IDs"), Preset.EquippedItemIds.Num(), 2);
		if (Preset.EquippedItemIds.Num() != 2)
		{
			continue;
		}
		TestEqual(TEXT("Every preset top uses the exact approved ID"), Preset.EquippedItemIds[0], FName(TEXT("starter_offwhite_top")));
		TestEqual(TEXT("Every preset bottom uses the exact approved ID"), Preset.EquippedItemIds[1], FName(TEXT("starter_offwhite_bottom")));
		EOddsWellStarterEquipmentSlot TopSlot = EOddsWellStarterEquipmentSlot::Bottom;
		EOddsWellStarterEquipmentSlot BottomSlot = EOddsWellStarterEquipmentSlot::Top;
		TestTrue(TEXT("Catalog top resolves"), ResolveOddsWellStarterEquipmentSlot(Preset.EquippedItemIds[0], TopSlot, Error));
		TestTrue(TEXT("Catalog bottom resolves"), ResolveOddsWellStarterEquipmentSlot(Preset.EquippedItemIds[1], BottomSlot, Error));
		TestTrue(TEXT("Top maps only to Top"), TopSlot == EOddsWellStarterEquipmentSlot::Top);
		TestTrue(TEXT("Bottom maps only to Bottom"), BottomSlot == EOddsWellStarterEquipmentSlot::Bottom);
	}

	FOddsWellStarterOutfitState State;
	const FName TopId = Presets[0].EquippedItemIds[0];
	const FName BottomId = Presets[0].EquippedItemIds[1];
	TestFalse(TEXT("Unknown equipment is rejected"), State.Equip(FName(TEXT("unknown_item")), EOddsWellStarterEquipmentSlot::Top, Error));
	TestFalse(TEXT("Unknown equipment reports an error"), Error.IsEmpty());
	TestFalse(TEXT("Top cannot be applied to Bottom"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestFalse(TEXT("Wrong-slot application reports an error"), Error.IsEmpty());
	TestFalse(TEXT("Incomplete outfit is rejected"), State.ValidateComplete(Error));
	TestFalse(TEXT("Missing slot reports an error"), Error.IsEmpty());
	TestTrue(TEXT("Top equips in Top"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error));
	TestFalse(TEXT("Duplicate Top assignment is rejected"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error));
	TestFalse(TEXT("Duplicate slot reports an error"), Error.IsEmpty());
	TestTrue(TEXT("Bottom equips in Bottom"), State.Equip(BottomId, EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestTrue(TEXT("Complete outfit validates"), State.ValidateComplete(Error));
	TestTrue(TEXT("Top removes independently"), State.Unequip(EOddsWellStarterEquipmentSlot::Top, Error));
	TestEqual(TEXT("Bottom remains after Top removal"), State.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom), BottomId);
	TestTrue(TEXT("Top restores independently"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error));
	TestTrue(TEXT("Bottom removes independently"), State.Unequip(EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestEqual(TEXT("Top remains after Bottom removal"), State.GetEquipped(EOddsWellStarterEquipmentSlot::Top), TopId);
	TestTrue(TEXT("Bottom restores independently"), State.Equip(BottomId, EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestTrue(TEXT("Restored outfit validates"), State.ValidateComplete(Error));
	TestTrue(TEXT("Top and Bottom component identities stay separate"), TopComponentName != BottomComponentName);
	TestEqual(TEXT("Walk calibration is unchanged"), WalkSpeed, 260.0f);
	TestEqual(TEXT("Run calibration is unchanged"), RunSpeed, 520.0f);
	TestEqual(TEXT("Jump calibration is unchanged"), JumpVelocity, 520.0f);
	return !HasAnyErrors();
}
#endif
