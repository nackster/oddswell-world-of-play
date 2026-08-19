#include "OddsWell.h"
#include "ReplayBenchmarkActor.h"
#include "Engine/World.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Modules/ModuleManager.h"

#if UE_BUILD_DEVELOPMENT
#include "CandidateBPolicySmoke.h"
#endif

IMPLEMENT_PRIMARY_GAME_MODULE(FOddsWellModule, OddsWell, "OddsWell");

void FOddsWellModule::StartupModule()
{
	FDefaultGameModuleImpl::StartupModule();
	const bool bReplayBenchmark = FParse::Param(FCommandLine::Get(), TEXT("ReplayBenchmark"));
#if UE_BUILD_DEVELOPMENT
	const bool bCandidateBPolicySmoke = OddsWellCandidateBPolicySmoke::IsCandidateBPolicySmokeRequested(FCommandLine::Get());
	if (bCandidateBPolicySmoke)
	{
		UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=FLAG_ACCEPTED|schema=1"));
	}
	if (bReplayBenchmark || bCandidateBPolicySmoke)
#else
	if (bReplayBenchmark)
#endif
	{
		WorldInitializedHandle = FWorldDelegates::OnPostWorldInitialization.AddRaw(this, &FOddsWellModule::HandleWorldInitialized);
	}
}

void FOddsWellModule::ShutdownModule()
{
	FWorldDelegates::OnPostWorldInitialization.Remove(WorldInitializedHandle);
	FDefaultGameModuleImpl::ShutdownModule();
}

void FOddsWellModule::HandleWorldInitialized(UWorld* World, const UWorld::InitializationValues IVS)
{
	if (World && World->IsGameWorld())
	{
		if (FParse::Param(FCommandLine::Get(), TEXT("ReplayBenchmark")))
		{
			World->SpawnActor<AReplayBenchmarkActor>();
		}
#if UE_BUILD_DEVELOPMENT
		if (OddsWellCandidateBPolicySmoke::IsCandidateBPolicySmokeRequested(FCommandLine::Get()))
		{
			OddsWellCandidateBPolicySmoke::BindToWorld(World);
		}
#endif
	}
}
