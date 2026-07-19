#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"
#include "Modules/ModuleManager.h"

class FOddsWellModule final : public FDefaultGameModuleImpl
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	void HandleWorldInitialized(UWorld* World, const UWorld::InitializationValues IVS);
	FDelegateHandle WorldInitializedHandle;
};
