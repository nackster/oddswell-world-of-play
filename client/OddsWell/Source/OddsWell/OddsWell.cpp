#include "OddsWell.h"
#include "ReplayBenchmarkActor.h"
#include "Engine/World.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FOddsWellModule, OddsWell, "OddsWell");

void FOddsWellModule::StartupModule()
{
	FDefaultGameModuleImpl::StartupModule();
	if (FParse::Param(FCommandLine::Get(), TEXT("ReplayBenchmark")))
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
		World->SpawnActor<AReplayBenchmarkActor>();
	}
}
