#pragma once

#include "CoreMinimal.h"
#include "CharacterPresetCatalog.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "OddsBucksLedger.h"
#include "PublicLeagueView.h"
#include "PlaceholderLocomotion.generated.h"

struct FOddsWellResolvedCharacterAppearance;

class UCameraComponent;
class UMaterialInstanceDynamic;
class USpringArmComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

USTRUCT()
struct FOddsWellSharedCityAppearance
{
	GENERATED_BODY()

	UPROPERTY()
	FName PresetId;

	UPROPERTY()
	FName TopItemId;

	UPROPERTY()
	FName BottomItemId;

	UPROPERTY()
	bool bOwnerSubmitted = false;
};

class FOddsWellStarterOutfitState
{
public:
	bool Equip(FName ItemId, EOddsWellStarterEquipmentSlot Slot, FString& OutError);
	bool Unequip(EOddsWellStarterEquipmentSlot Slot, FString& OutError);
	bool ValidateComplete(FString& OutError) const;
	FName GetEquipped(EOddsWellStarterEquipmentSlot Slot) const;
	void Reset();

private:
	FName EquippedTop;
	FName EquippedBottom;
};

UCLASS()
class ODDSWELL_API AOddsWellPlaceholderCharacter final : public ACharacter
{
	GENERATED_BODY()

public:
	AOddsWellPlaceholderCharacter();
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void PossessedBy(AController* NewController) override;
	virtual void PawnClientRestart() override;
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	void AssignSharedCityPlayerNumber(int32 PlayerNumber);
	int32 GetSharedCityPlayerNumber() const { return SharedCityPlayerNumber; }
	const FOddsWellSharedCityAppearance& GetSharedCityAppearance() const { return SharedCityAppearance; }
	bool HasValidSharedCityAppearance() const;
	bool HasSubmittedSharedCityAppearance() const { return SharedCityAppearance.bOwnerSubmitted; }
	bool IsTicketBoothPromptVisible() const;
	bool IsTicketBoothMenuVisible() const { return bSportsbookOfferVisible; }
	int32 GetTicketBoothMarketPage() const { return SportsbookMarketPage; }
	const FOddsWellMatchWinnerOfferPreview* GetTicketBoothOffer() const { return SportsbookOfferPreview.Get(); }
	const FOddsWellCanonicalPendingMatchWinnerReceipt* GetTicketBoothCanonicalReceipt() const { return SportsbookCanonicalReceipt.Get(); }
	const FOddsWellCanonicalSettledLossReceipt* GetTicketBoothSettledLossReceipt() const { return SportsbookSettledLossReceipt.Get(); }
	bool CanReviewTicketBoothBetSlip() const;
	int32 GetTicketBoothReviewSelectionIndex() const { return TicketBoothReviewSelectionIndex; }
	int64 GetTicketBoothReviewStake() const { return TicketBoothReviewStake; }
	int64 GetTicketBoothReviewGrossReturn() const;
	int64 GetTicketBoothCurrentBalance() const;
	FString GetTicketBoothReviewText() const;
	void SelectTicketBoothReviewTeam(int32 SelectionIndex);
	void DecreaseTicketBoothReviewStake();
	void IncreaseTicketBoothReviewStake();
	void SetTicketBoothMarketPage(int32 Page);
	void CloseTicketBoothMenu();

protected:
	virtual void BeginPlay() override;

private:
	void MoveForward(float Value);
	void MoveRight(float Value);
	void PollKeyboardMovement();
	void LookYaw(float Value);
	void LookPitchMouse(float Value);
	void LookPitchController(float Value);
	void StartRun();
	void StopRun();
	void StartJump();
	void StopJump();
	void RunQa(float DeltaSeconds);
	void FinishQa(bool bPassed);
	void RunSundaleRouteQa(float DeltaSeconds);
	void FinishSundaleRouteQa(bool bPassed);
	void RunSharedCityQa(float DeltaSeconds);
	void PollJobInteraction();
	void PollStudioInteraction();
	void PollStadiumInteraction();
	void PollSportsbookInteraction();
	void ToggleLeagueView();
	void PreviousLeaguePage();
	void NextLeaguePage();
	void ShowLeaguePage();
	void RefreshSportsbookOfferPreview();
	void ToggleSportsbookOfferPreview();
	void ShowSportsbookOfferPreview();
	void PreviousSportsbookMarketPage();
	void NextSportsbookMarketPage();
	void SelectPreviousTicketBoothReviewTeam();
	void SelectNextTicketBoothReviewTeam();
	void ResetTicketBoothReview();
	void SetTicketBoothInputMode(bool bMenuOpen);
	void ToggleSportsbookQaWager();
	void ShowSportsbookQaWager();
	void ToggleSportsbookReceipt();
	void ShowSportsbookReceipt();
	void SelectPreviousSportsbookQaTeam();
	void SelectNextSportsbookQaTeam();
	void DecreaseSportsbookQaStake();
	void IncreaseSportsbookQaStake();
	void ConfirmSportsbookQaWager();
	FString BuildSportsbookQaWagerText() const;
	FString BuildSportsbookReceiptText() const;
	void RunStudioQa(float DeltaSeconds);
	void RunStadiumQa(float DeltaSeconds);
	void RunSportsbookOfferQa(float DeltaSeconds);
	void RunSportsbookWagerQa(float DeltaSeconds);
	void RunSportsbookReceiptQa(float DeltaSeconds);
	void RunJobQa(float DeltaSeconds);
	void RunCameraOrbitQa(float DeltaSeconds);
	bool ApplySavedOrFallbackAppearance();
	bool ResolveLocalAppearance(FOddsWellResolvedCharacterAppearance& OutAppearance, FString& OutSource, FString& OutError) const;
	bool ApplyResolvedAppearance(const FOddsWellResolvedCharacterAppearance& Appearance, const FString& Source);
	bool ApplySharedCityAppearance(const FString& Source);
	void SubmitLocalSharedCityAppearance();
	void SetAuthoritativeSharedCityAppearance(FName PresetId, FName TopItemId, FName BottomItemId, bool bOwnerSubmitted, const FString& Source);
	void SyncOutfitComponents();
	void SyncSharedCityNameplate();
	void RunOutfitQa(float DeltaSeconds);
	void ReportOutfitError(const FString& Error) const;
	void ReportAppearanceError(const FString& Error) const;

	UFUNCTION()
	void OnRep_SharedCityPlayerNumber();

	UFUNCTION()
	void OnRep_SharedCityAppearance();

	UFUNCTION(Server, Reliable)
	void ServerSetSharedCityAppearance(FName PresetId, FName TopItemId, FName BottomItemId);

	UFUNCTION(Server, Reliable)
	void ServerCompletePlaceholderJob();

	UFUNCTION(Client, Reliable)
	void ClientConfirmPlaceholderJob(bool bCompleted, bool bCredited, bool bPayoutReady, int64 Balance, int64 RetryAfterSeconds);

	UFUNCTION(Server, Reliable)
	void ServerConfirmSportsbookQaWager(const FString& OfferedTeam, int64 Stake);

	UFUNCTION(Client, Reliable)
	void ClientConfirmSportsbookQaWager(bool bAccepted, bool bDuplicate, const FString& RequestId, const FString& OfferedTeam, int64 Stake, int64 Balance, const FString& Error);

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> PrimitiveBody;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> PrimitiveHead;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> StarterOutfitTop;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> StarterOutfitBottom;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> StarterOutfitMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> PrimitiveSkinMaterial;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UTextRenderComponent> SharedCityNameplate;

	UPROPERTY(ReplicatedUsing=OnRep_SharedCityPlayerNumber)
	int32 SharedCityPlayerNumber = 0;

	UPROPERTY(ReplicatedUsing=OnRep_SharedCityAppearance)
	FOddsWellSharedCityAppearance SharedCityAppearance;

	FOddsWellStarterOutfitState StarterOutfitState;
	FVector QaStartLocation = FVector::ZeroVector;
	float QaElapsed = 0.0f;
	float QaMaxZ = 0.0f;
	float QaWalkPeak = 0.0f;
	float QaRunPeak = 0.0f;
	float QaStartYaw = 0.0f;
	double QaExitAt = 0.0;
	bool bQaEnabled = false;
	bool bQaStarted = false;
	bool bQaJumpIssued = false;
	bool bQaFinished = false;
	bool bQaAutoExit = false;
	float OutfitQaElapsed = 0.0f;
	int32 OutfitQaStage = 0;
	bool bOutfitQaEnabled = false;
	bool bAppearanceQa = false;
	bool bAppearanceQaCleanup = false;
	FVector SundaleRouteStart = FVector::ZeroVector;
	FVector SundalePreviousLocation = FVector::ZeroVector;
	float SundaleRouteElapsed = 0.0f;
	float SundaleSegmentElapsed = 0.0f;
	float SundaleTravelDistance = 0.0f;
	float SundaleMinZ = 0.0f;
	float SundaleMaxZ = 0.0f;
	int32 SundaleRouteIndex = 0;
	bool bSundaleRouteQa = false;
	bool bSundaleRouteRun = false;
	bool bSundaleRouteStarted = false;
	bool bSundaleRouteFinished = false;
	float SharedCityQaElapsed = 0.0f;
	double SharedCityQaExitAt = 0.0;
	int32 SharedCityQaTargetClients = 2;
	bool bSharedCityQa = false;
	bool bSharedCityCapacityQa = false;
	bool bSharedCityCapacityLogged = false;
	bool bSharedCityQaVisibleLogged = false;
	bool bSharedCityQaAppearanceLogged = false;
	bool bSharedCityAppearanceSubmitted = false;
	FVector StudioQaStartLocation = FVector::ZeroVector;
	float StudioQaElapsed = 0.0f;
	bool bStudioInteractionArmed = false;
	bool bStudioQa = false;
	bool bStudioQaInteriorStarted = false;
	bool bStudioPersistenceQa = false;
	bool bStudioPersistenceQaVerify = false;
	bool bOwnsStudio = false;
	bool bHousingGoalsLogged = false;
	float JobQaElapsed = 0.0f;
	bool bPlaceholderShiftCompleted = false;
	bool bJobInteractionArmed = false;
	bool bJobQa = false;
	bool bJobQaRejectionProven = false;
	bool bJobQaFirstCreditProven = false;
	bool bJobPayoutQaVerify = false;
	bool bJobRecoveryQa = false;
	bool bJobRecoveryQaVerify = false;
	bool bJobRecoveryCooldownProven = false;
	int32 JobRecoveryQaStage = 0;
	float StadiumQaElapsed = 0.0f;
	int32 StadiumQaWaypointIndex = 0;
	bool bStadiumInteractionArmed = false;
	bool bStadiumQa = false;
	bool bStadiumQaInteriorStarted = false;
	bool bStadiumQaMarkerReached = false;
	TUniquePtr<FOddsWellPublicLeagueSnapshot> PublicLeagueSnapshot;
	TUniquePtr<FOddsWellMatchWinnerOfferPreview> SportsbookOfferPreview;
	TUniquePtr<FOddsWellCanonicalPendingMatchWinnerReceipt> SportsbookCanonicalReceipt;
	TUniquePtr<FOddsWellCanonicalSettledLossReceipt> SportsbookSettledLossReceipt;
	TUniquePtr<FOddsWellMatchWinnerOffer> SportsbookQaOffer;
	TUniquePtr<FOddsWellPendingQaMatchWinnerReceipt> SportsbookReceipt;
	int32 PublicLeaguePage = 0;
	bool bPublicLeagueVisible = false;
	bool bPublicLeagueQa = false;
	bool bPublicLeagueQaCaptured = false;
	float PublicLeagueQaElapsed = 0.0f;
	float SportsbookOfferQaElapsed = 0.0f;
	int32 SportsbookOfferQaStage = 0;
	int32 SportsbookOfferQaLedgerEntries = 0;
	int64 SportsbookOfferQaBalance = 0;
	bool bSportsbookInteractionArmed = false;
	bool bAtSportsbookInteraction = false;
	bool bSportsbookOfferVisible = false;
	bool bSportsbookOfferQa = false;
	bool bCanonicalPendingReceiptQa = false;
	bool bCanonicalPostLockQa = false;
	bool bCanonicalSettledLossReceiptQa = false;
	bool bCanonicalBetSlipReviewQa = false;
	bool bCanonicalMissingHeldOpenTipoffQa = false;
	int32 SportsbookMarketPage = 0;
	int32 TicketBoothReviewSelectionIndex = INDEX_NONE;
	int64 TicketBoothReviewStake = 10;
	int32 SportsbookQaSelectionIndex = 0;
	int64 SportsbookQaStake = 10;
	int64 SportsbookQaResultingBalance = 0;
	FString SportsbookQaAcceptedRequestId;
	FString SportsbookQaAcceptedTeam;
	float SportsbookWagerQaElapsed = 0.0f;
	int32 SportsbookWagerQaStage = 0;
	bool bSportsbookQaWagerVisible = false;
	bool bSportsbookQaReviewing = false;
	bool bSportsbookQaAccepted = false;
	bool bSportsbookQaDuplicate = false;
	bool bSportsbookWagerQaMode = false;
	bool bSportsbookWagerQaAuto = false;
	bool bSportsbookWagerQaVerify = false;
	float SportsbookReceiptQaElapsed = 0.0f;
	bool bSportsbookReceiptVisible = false;
	bool bSportsbookReceiptQaMode = false;
	bool bSportsbookReceiptQaAuto = false;
	FVector CameraOrbitQaStartLocation = FVector::ZeroVector;
	float CameraOrbitQaElapsed = 0.0f;
	float CameraOrbitQaPreviousYaw = 0.0f;
	float CameraOrbitQaSweep = 0.0f;
	bool bCameraOrbitQa = false;
	bool bCameraOrbitQaStarted = false;
};

UCLASS()
class ODDSWELL_API AOddsWellSportsbookHUD final : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;
	virtual void NotifyHitBoxClick(FName BoxName) override;

private:
	AOddsWellPlaceholderCharacter* GetOddsWellCharacter() const;
	void DrawTicketBoothPrompt();
	void DrawTicketBoothUnavailableMenu();
	void DrawTicketBoothSettledLossReceipt(const FOddsWellCanonicalSettledLossReceipt& Receipt);
	void DrawTicketBoothMenu(const AOddsWellPlaceholderCharacter& Character, const FOddsWellMatchWinnerOfferPreview& Offer);
	void DrawMarketCard(const FString& Title, const FString& Subtitle, float X, float Y, float Width, float Height, bool bAvailable);
};

UCLASS()
class ODDSWELL_API AOddsWellLocomotionGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellLocomotionGameMode();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void PostLogin(APlayerController* NewPlayer) override;
	virtual void Logout(AController* Exiting) override;
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&) override;
	bool TryCreditPlaceholderJob(bool& bOutCredited, int64& OutBalance, int64& OutRetryAfterSeconds, FString& OutCommandId, FString& OutError);
	EOddsWellMatchWinnerRequestResult AcceptSportsbookQaWager(const FString& OfferedTeam, int64 Stake, FOddsWellMatchWinnerRequestRecord& OutRecord, int64& OutBalance, FString& OutError);
	bool RunSportsbookQaWagerAudit(int32& OutLedgerEntries, int32& OutRequests, int64& OutBalance, FString& OutError);
	bool AdvanceOddsBucksQaClock(int64 Seconds);
	int32 GetOddsBucksEntryCount() const { return OddsBucksLedger.GetEntries().Num(); }
	int32 GetMatchWinnerRequestCount() const { return MatchWinnerRequestCount; }
	int64 GetOddsBucksBalance() const { return OddsBucksLedger.GetBalance(); }
	int64 GetNextJobPayoutUnixSeconds() const { return NextJobPayoutUnixSeconds; }
	int64 GetOddsBucksNowUnixSeconds() const;
	bool WasOddsBucksLoadedFromDisk() const { return bOddsBucksLoadedFromDisk; }

private:
	void PublishOddsBucksReconciliation();
	void RunSportsbookLockQa();
	void RunSportsbookCancellationQa();
	void RunSportsbookVoidDecisionQa();
	void RunSportsbookVoidFinalizationQa();
	FOddsWellOddsBucksLedger OddsBucksLedger;
	TMap<int32, FVector> SharedCityQaStartLocations;
	FOddsWellSharedCityAppearance SharedCityReconnectExpectedAppearance;
	double SharedCityQaExitAt = 0.0;
	int32 NextSharedCityPlayerNumber = 1;
	int32 SharedCityQaTargetClients = 2;
	int32 SharedCityReconnectExpectedPlayerNumber = 0;
	bool bSharedCityQa = false;
	bool bSharedCityQaStarted = false;
	bool bSharedCityQaPassed = false;
	bool bSharedCityReconnectQa = false;
	bool bSharedCityReconnectLeaveObserved = false;
	bool bSharedCityReconnectPassed = false;
	bool bSharedCityCapacityQa = false;
	bool bOddsBucksReady = false;
	bool bOddsBucksQaSlot = false;
	bool bOddsBucksLoadedFromDisk = false;
	bool bSportsbookWagerQa = false;
	bool bSportsbookLockQa = false;
	bool bSportsbookLockQaVerify = false;
	bool bSportsbookLockQaDone = false;
	int32 SportsbookLockQaStage = 0;
	bool bSportsbookCancellationQa = false;
	bool bSportsbookCancellationQaVerify = false;
	bool bSportsbookCancellationQaDone = false;
	int32 SportsbookCancellationQaStage = 0;
	bool bSportsbookVoidDecisionQa = false;
	bool bSportsbookVoidDecisionQaVerify = false;
	bool bSportsbookVoidDecisionQaDone = false;
	bool bSportsbookVoidFinalizationQa = false;
	bool bSportsbookVoidFinalizationQaVerify = false;
	bool bSportsbookVoidFinalizationQaDone = false;
	int32 MatchWinnerRequestCount = 0;
	int64 NextJobPayoutUnixSeconds = 0;
	int64 OddsBucksQaNowUnixSeconds = 0;
};

UCLASS()
class ODDSWELL_API AOddsWellStudioGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellStudioGameMode();
	virtual void BeginPlay() override;
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&) override;
};

UCLASS()
class ODDSWELL_API AOddsWellStadiumGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellStadiumGameMode();
	virtual void BeginPlay() override;
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&) override;
};
