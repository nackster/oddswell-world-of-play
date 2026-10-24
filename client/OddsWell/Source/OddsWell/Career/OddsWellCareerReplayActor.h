#pragma once

#include "CoreMinimal.h"
#include "Career/OddsWellCareer.h"
#include "GameFramework/Actor.h"
#include "OddsWellCareerReplayActor.generated.h"

class UCameraComponent;
class USceneComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

// Presents one career game from its regenerated authoritative event log. Watching or skipping
// never changes the result: the frames come from the same sealed simulation as the standings.
UCLASS()
class ODDSWELL_API AOddsWellCareerReplayActor : public AActor
{
	GENERATED_BODY()

public:
	AOddsWellCareerReplayActor();
	virtual void Tick(float DeltaSeconds) override;

	bool StartGame(int32 GameId, FString& OutError);
	void SkipToFinal();
	bool IsComplete() const { return bComplete; }
	const FOddsWellCareerReplay& GetReplay() const { return Replay; }
	const FOddsWellCareerReplayFrame* GetCurrentFrame() const;
	float GetProgress() const;

private:
	void CreateMarkers();
	void DisplayFrame(int32 FrameIndex);
	void SetMarkerState(const FString& PlayerName, float Scale, float HeightOffset);

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UCameraComponent> BroadcastCamera;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UTextRenderComponent> Scoreboard;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> Markers;

	FOddsWellCareerReplay Replay;
	TArray<FVector> MarkerLocations;
	TMap<FString, int32> PlayerMarkerIndices;
	float FrameInterval = 0.4f;
	float Accumulator = 0.0f;
	int32 NextFrame = 0;
	int32 CurrentFrame = INDEX_NONE;
	bool bStarted = false;
	bool bComplete = false;
};
