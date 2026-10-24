#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ReplayBenchmarkActor.generated.h"

class UCameraComponent;
class USceneComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

struct FReplayBenchmarkFrame
{
	FString Kind;
	FString Label;
	FString Offense;
	FString Actor;
	FString Target;
	int32 ClockSeconds = 0;
	int32 HomeScore = 0;
	int32 AwayScore = 0;
};

UCLASS()
class ODDSWELL_API AReplayBenchmarkActor : public AActor
{
	GENERATED_BODY()

public:
	AReplayBenchmarkActor();
	virtual void Tick(float DeltaSeconds) override;

protected:
	virtual void BeginPlay() override;

private:
	bool LoadFixture();
	bool ConfigureViewMode();
	void SkipToFinal();
	void CreateMarkers();
	void DisplayFrame(int32 FrameIndex);
	void SetMarkerState(const FString& PlayerName, float Scale, float HeightOffset);

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UCameraComponent> BenchmarkCamera;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UTextRenderComponent> StatusText;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> Markers;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UTextRenderComponent>> PlayerLabels;

	TArray<FVector> MarkerLocations;
	TArray<FReplayBenchmarkFrame> Frames;
	TArray<FString> HomePlayers;
	TArray<FString> AwayPlayers;
	TMap<FString, int32> PlayerMarkerIndices;
	FString HomeTeam;
	FString AwayTeam;
	FString ReplaySha256;
	FString ViewMode = TEXT("watch");
	float ReplayInterval = 0.1f;
	float Accumulator = 0.0f;
	float PresentationElapsed = 0.0f;
	float ExitDelay = 0.0f;
	int32 NextFrame = 0;
	int32 StartFrame = 1;
	int32 RenderedFrameCount = 0;
	int32 QASkipAfterFrame = 0;
	int32 SkipFromFrame = 0;
	bool bAutoExit = false;
	bool bCaptureProof = false;
	bool bIntervalOverridden = false;
	bool bComplete = false;
};
