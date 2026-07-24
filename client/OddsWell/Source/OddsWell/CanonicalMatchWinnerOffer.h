#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CanonicalMatchWinnerOffer.generated.h"

struct FOddsWellMatchWinnerOfferPreview;
struct FOddsWellMatchWinnerRequestRecord;
struct FOddsWellCanonicalPendingMatchWinnerReceipt;
struct FOddsWellMatchWinnerLockRecord;
enum class EOddsWellMatchWinnerRequestResult : uint8;
enum class EOddsWellMatchWinnerLockResult : uint8;
enum class EOddsWellCanonicalPendingReceiptResult : uint8;

UCLASS()
class ODDSWELL_API UOddsWellCanonicalMatchWinnerOfferSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString CanonicalOfferJson;
};

struct FOddsWellCanonicalMatchWinnerOfferRecord
{
	FString OfferId;
	FString CanonicalOfferJson;
	int64 LockUnixSeconds = 0;
};

enum class EOddsWellCanonicalMatchWinnerOfferResult : uint8
{
	Created,
	Duplicate,
	Rejected
};

ODDSWELL_API EOddsWellCanonicalMatchWinnerOfferResult CreateOddsWellCanonicalMatchWinnerOffer(
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError);
ODDSWELL_API bool LoadOddsWellCanonicalMatchWinnerOffer(
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError);
ODDSWELL_API bool LoadOddsWellCanonicalMatchWinnerOfferPreview(
	FOddsWellMatchWinnerOfferPreview& OutPreview,
	FString& OutError);
ODDSWELL_API EOddsWellCanonicalPendingReceiptResult LoadOddsWellCanonicalPendingMatchWinnerReceipt(
	FOddsWellCanonicalPendingMatchWinnerReceipt& OutReceipt,
	FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerRequestResult AcceptOddsWellCanonicalMatchWinnerRequest(
	const FString& OfferedOfferId,
	const FString& OfferedTeam,
	int64 Stake,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerLockResult LockOddsWellCanonicalMatchWinnerRequestAtGameStart(
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError);
