#pragma once

#if UE_BUILD_DEVELOPMENT

#include "CoreTypes.h"

class UWorld;

namespace OddsWellCandidateBPolicySmoke
{
	bool IsCandidateBPolicySmokeRequested(const TCHAR* CommandLine);
	void BindToWorld(UWorld* World);
}

#endif
