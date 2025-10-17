/*
BLUX Guard YARA Rules Index

This file serves as the primary index for YARA rules used by the BLUX Guard
nano-swarm system.  It can include rules directly or import rules from
other files within the rules directory.

Author: Outer Void Team
Date: 2024-01-01

Rules should be organized by category and include descriptive metadata to
facilitate maintenance and analysis.
*/

/* --- Basic Example Rule --- */
rule ExampleMalware
{
    meta:
        description = "Detects a known malware signature"
        author = "Outer Void Team"
        date = "2024-01-01"
        malware_family = "ExampleFamily"
        confidence = 75 // Percentage
    strings:
        $mz = { 4D 5A }  // PE Header
        $string1 = "SuspiciousString1"
        $string2 = "SuspiciousString2"
    condition:
        $mz and $string1 and $string2
}

/* --- Rule Importing Example --- */
/*
import "rules/phishing_rules.yar" // Relative to this file, adjust path as needed
import "rules/exploit_rules.yar"
*/

/* --- More Rule Examples --- */

rule DetectPotentiallyUnwantedApp
{
    meta:
        description = "Detects a Potentially Unwanted Application (PUA) based on common characteristics"
        author = "Outer Void Team"
        date = "2024-01-01"
        threat_level = "low"
    strings:
        $string1 = "InstallShield"
        $string2 = "OpenCandy"
        $string3 = "Toolbar"
    condition:
        all of them
}

rule DetectSuspiciousFileOperation
{
    meta:
        description = "Detects suspicious file operations like creating executables in temp directories"
        author = "Outer Void Team"
        date = "2024-01-01"
        threat_level = "medium"
    strings:
        $api1 = "CreateFile"
        $api2 = "WriteFile"
        $path = "%TEMP%\\*.exe" nocase
    condition:
        $api1 and $api2 and $path
}
