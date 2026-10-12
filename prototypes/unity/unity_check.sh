#!/usr/bin/env bash
# Local compile check of the Unity C# sources against UnityEngine module reference assemblies
# (NuGet UnityEngine.Modules) + stubs for UnityEngine.UI / UnityEditor. Catches syntax/type errors
# without a Unity install; Unity-specific serialization/runtime behaviour still needs the real editor.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${TMPDIR:-/tmp}/unity_check"
mkdir -p "$WORK"
cat > "$WORK/check.csproj" <<EOF
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <Nullable>disable</Nullable>
    <NoWarn>CS0414;CS0649;CS0169;CS0067;CS0618</NoWarn>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="UnityEngine.Modules" Version="2021.3.33" />
    <Compile Include="$ROOT/unity/Assets/**/*.cs" />
    <Compile Include="$ROOT/tools/unity_stubs/*.cs" />
  </ItemGroup>
</Project>
EOF
cd "$WORK"
dotnet build check.csproj -nologo -v q -clp:NoSummary 2>&1 | grep -E "error|warning CS0(1|2)|Build succeeded" | sort -u || true
dotnet build check.csproj -nologo -v q > /dev/null 2>&1 && echo "COMPILE OK" || { echo "COMPILE FAILED"; exit 1; }
