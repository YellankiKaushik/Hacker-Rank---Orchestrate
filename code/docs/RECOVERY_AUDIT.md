# Recovery audit — source-supported links and remaining ambiguity

Measured 2026-10-24T17:01:38.841587+00:00, continuing commit 01beaa1. This report uses participant observations and actual run diagnostics; sample references are evaluator-only. No ID suffix, case numbering, file naming, temporal-neighbor matching or answer-pattern assignment was used in inference.

## P1–P4 findings and implemented repairs

1. The original engine did not traverse explicit `source_resource_id` fields. The new dated relationship graph combines that field with independent activity owner-system metadata, treating operation success/failure only as a claim. The actual structured corpus exposes three such links, all in the dedicated search snapshot. This repaired a public-sample account verification sequence; it did not recover the blocked full-dataset cluster.
2. Inventory exports are scoped batches. An attempted cross-batch global absence rule wrongly cleared a known remaining profile and was reverted. The regression suite now prevents unrelated batch exports proving absence. Dedicated physical-table captures can answer an already-grounded resource-key query; ordinary inventory batches still require a linked source scope.
3. Source/proof IDs, observation/capture times, owner scope, lookup locators and reference paths are retained as binding provenance. Current/historical phone formats normalize to a conservative E.164 key. A stable subject conflicting with the matching email is rejected rather than merged.
4. OCR can replace an underscore with a space. Structural separator normalization is allowed only for an already-supplied catalog label and with word boundaries; it recovered a retained tombstone and security-record view. It does not perform fuzzy name or numeric-ID matching.
5. GhostGuard now distinguishes rejection categories and performs one targeted reread of at most four admissible source files. A regression with a deliberately damaged lookup index is repaired from raw source, then passes independent source review. Actual full-run rereads did not supply the missing subject selectors: `{'MISSING_PROFILE_LINK_OR_PROOF': 97, 'MISSING_EVIDENCE': 1}` remain blocked.
6. An older still-present replica is not cleared by a later primary-only absence. A storage/existence listing does not supersede known restore-access configuration. Explicit readback activity cannot support a forged opposite state. Validator shape checks reject malformed input with controlled errors.

## Recovery outcome

- Previously blocked: 98 evaluation cases.
- Defensibly recovered from that archived set: [].
- Newly blocked relative to that set: [].
- Accepted rows: 420/518; remaining: 98.
- Missing-profile cluster diagnostic reasons: `{'NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES': 43, 'ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE': 25, 'MISSING_SUBJECT_TO_RESOURCE_LINK': 29}`.
- Primary versus reviewed public statuses: 29/32 versus 24/32; exact arrays 9/32 versus 9/32. No large accuracy recovery is claimed.

## Why orphan readbacks remain unresolved

A 404/anonymous row can prove a state for the supplied resource key without saying whose key it is. A retained journal in the same batch establishes that the person occurs in that batch, but does not identify which anonymous lookup belongs to that person. Batch position and one-to-one assignments are not stated in the source schema. Multiple assignments of anonymous resource rows can therefore remain consistent with the visible identifiers. A deletion-worker event near a case's report time does not supply the missing subject link in this global stream, which also contains unrelated people. A later capture with an earlier observation is still excluded when its capture is after the case cutoff.

The table records real candidate rows in admitted, linked sources without assigning any candidate to a subject. “Zero candidates” does not establish deletion. Some sources contain no root-account observation at all; others contain unbound root readbacks. This is an input/provenance limitation at this checkpoint, not a claim that every official file is defective or that no future parser improvement is possible.

| Case | Linked admitted sources | Unbound root candidates | Future-only root sources excluded | Reason | Reread sources attempted |
|---|---|---|---|---|---|
| case_103 | evidence_10 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_10 |
| case_107 | evidence_10 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_10 |
| case_108 | evidence_10 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_10 |
| case_111 | evidence_10 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_10 |
| case_112 | evidence_10 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_10 |
| case_126 | evidence_87 | evidence_87:account_6673/PRESENT | evidence_12 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_87 |
| case_127 | evidence_87 | evidence_87:account_6673/PRESENT | evidence_12 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_87 |
| case_150 | evidence_86 | evidence_86:account_3897/ABSENT, evidence_86:account_874/ABSENT, evidence_86:account_8854/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_86 |
| case_151 | evidence_86 | evidence_86:account_3897/ABSENT, evidence_86:account_874/ABSENT, evidence_86:account_8854/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_86 |
| case_152 | evidence_86 | evidence_86:account_3897/ABSENT, evidence_86:account_874/ABSENT, evidence_86:account_8854/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_86 |
| case_155 | evidence_15 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_15 |
| case_157 | evidence_15 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_15 |
| case_162 | evidence_15 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_15 |
| case_175 | evidence_84 | evidence_84:account_8423/PRESENT | evidence_17 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_84 |
| case_178 | evidence_84 | evidence_84:account_8423/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_84 |
| case_183 | evidence_83 | evidence_83:account_4854/ABSENT, evidence_83:account_5375/PRESENT, evidence_83:account_5848/PRESENT, evidence_83:account_7063/ABSENT, evidence_83:account_9317/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_83 |
| case_190 | evidence_83 | evidence_83:account_4854/ABSENT, evidence_83:account_5375/PRESENT, evidence_83:account_5848/PRESENT, evidence_83:account_7063/ABSENT, evidence_83:account_9317/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_83 |
| case_191 | evidence_83 | evidence_83:account_4854/ABSENT, evidence_83:account_5375/PRESENT, evidence_83:account_5848/PRESENT, evidence_83:account_7063/ABSENT, evidence_83:account_9317/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_83 |
| case_204 | evidence_20 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_20 |
| case_206 | evidence_20 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_20 |
| case_213 | evidence_81 | none | evidence_21 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_81 |
| case_215 | evidence_81 | none | evidence_21 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_81 |
| case_218 | evidence_81 | none | evidence_21 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_81 |
| case_219 | evidence_81 | none | evidence_21 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_81 |
| case_221 | evidence_81 | none | evidence_21 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_81 |
| case_225 | evidence_80 | evidence_80:account_392/ABSENT, evidence_80:account_5479/PRESENT, evidence_80:account_669/ABSENT, evidence_80:account_7324/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_80 |
| case_226 | evidence_80 | evidence_80:account_392/ABSENT, evidence_80:account_5479/PRESENT, evidence_80:account_669/ABSENT, evidence_80:account_7324/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_80 |
| case_231 | evidence_80 | evidence_80:account_392/ABSENT, evidence_80:account_5479/PRESENT, evidence_80:account_669/ABSENT, evidence_80:account_7324/ABSENT | evidence_22 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_80 |
| case_243 | evidence_78 | evidence_78:account_2981/PRESENT, evidence_78:account_4181/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_78 |
| case_244 | evidence_78 | evidence_78:account_2981/PRESENT, evidence_78:account_4181/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_78 |
| case_253 | evidence_24 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_24 |
| case_257 | evidence_24 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_24 |
| case_260 | evidence_24 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_24 |
| case_274 | evidence_77 | evidence_77:account_4853/ABSENT, evidence_77:account_6575/ABSENT, evidence_77:account_731/ABSENT, evidence_77:account_8689/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_77 |
| case_276 | evidence_77 | evidence_77:account_4853/ABSENT, evidence_77:account_6575/ABSENT, evidence_77:account_731/ABSENT, evidence_77:account_8689/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_77 |
| case_277 | evidence_77 | evidence_77:account_4853/ABSENT, evidence_77:account_6575/ABSENT, evidence_77:account_731/ABSENT, evidence_77:account_8689/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_77 |
| case_294 | evidence_75 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_75 |
| case_295 | evidence_75 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_75 |
| case_297 | evidence_75 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_75 |
| case_299 | evidence_75 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_75 |
| case_304 | evidence_29 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_29 |
| case_308 | evidence_29 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_29 |
| case_309 | evidence_29 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_29 |
| case_313 | evidence_74 | evidence_74:account_2088/ABSENT, evidence_74:account_591/ABSENT, evidence_74:account_8264/ABSENT, evidence_74:account_9354/ABSENT | evidence_30 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_74 |
| case_314 | evidence_74 | evidence_74:account_2088/ABSENT, evidence_74:account_591/ABSENT, evidence_74:account_8264/ABSENT, evidence_74:account_9354/ABSENT | evidence_30 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_74 |
| case_319 | evidence_74 | evidence_74:account_2088/ABSENT, evidence_74:account_591/ABSENT, evidence_74:account_8264/ABSENT, evidence_74:account_9354/ABSENT | evidence_30 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_74 |
| case_322 | evidence_74 | evidence_74:account_2088/ABSENT, evidence_74:account_591/ABSENT, evidence_74:account_8264/ABSENT, evidence_74:account_9354/ABSENT | evidence_30 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_74 |
| case_335 | evidence_72 | evidence_72:account_2475/PRESENT | evidence_31 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_72 |
| case_336 | evidence_72 | evidence_72:account_2475/PRESENT | evidence_31 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_72 |
| case_339 | evidence_72 | evidence_72:account_2475/PRESENT | evidence_31 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_72 |
| case_343 | evidence_71 | evidence_71:account_1949/ABSENT, evidence_71:account_5059/ABSENT, evidence_71:account_5214/ABSENT, evidence_71:account_8834/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_71 |
| case_345 | evidence_71 | evidence_71:account_1949/ABSENT, evidence_71:account_5059/ABSENT, evidence_71:account_5214/ABSENT, evidence_71:account_8834/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_71 |
| case_346 | evidence_71 | evidence_71:account_1949/ABSENT, evidence_71:account_5059/ABSENT, evidence_71:account_5214/ABSENT, evidence_71:account_8834/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_71 |
| case_351 | evidence_71 | evidence_71:account_1949/ABSENT, evidence_71:account_5059/ABSENT, evidence_71:account_5214/ABSENT, evidence_71:account_8834/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_71 |
| case_354 | evidence_33 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_33 |
| case_362 | evidence_33 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_33 |
| case_393 | evidence_69 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_69 |
| case_395 | evidence_69 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_69 |
| case_398 | evidence_69 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_69 |
| case_403 | evidence_38 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_38 |
| case_408 | evidence_38 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_38 |
| case_409 | evidence_38 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_38 |
| case_411 | evidence_38 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_38 |
| case_412 | evidence_38 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_38 |
| case_423 | evidence_68 | evidence_68:account_2420/ABSENT, evidence_68:account_2696/ABSENT, evidence_68:account_4204/PRESENT, evidence_68:account_6006/ABSENT, evidence_68:account_8461/ABSENT | evidence_40 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_68 |
| case_424 | evidence_68 | evidence_68:account_2420/ABSENT, evidence_68:account_2696/ABSENT, evidence_68:account_4204/PRESENT, evidence_68:account_6006/ABSENT, evidence_68:account_8461/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_68 |
| case_427 | evidence_68 | evidence_68:account_2420/ABSENT, evidence_68:account_2696/ABSENT, evidence_68:account_4204/PRESENT, evidence_68:account_6006/ABSENT, evidence_68:account_8461/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_68 |
| case_430 | evidence_68 | evidence_68:account_2420/ABSENT, evidence_68:account_2696/ABSENT, evidence_68:account_4204/PRESENT, evidence_68:account_6006/ABSENT, evidence_68:account_8461/ABSENT | evidence_40 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_68 |
| case_448 | evidence_66 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_66 |
| case_45 | evidence_37, evidence_55 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_37, evidence_55 |
| case_452 | evidence_66 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_66 |
| case_456 | evidence_43 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_43 |
| case_457 | evidence_43 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_43 |
| case_458 | evidence_43 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_43 |
| case_462 | evidence_43 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_43 |
| case_463 | evidence_65 | evidence_65:account_1698/ABSENT, evidence_65:account_2437/ABSENT, evidence_65:account_2480/ABSENT, evidence_65:account_3653/PRESENT, evidence_65:account_7023/ABSENT | evidence_44 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_65 |
| case_464 | evidence_65 | evidence_65:account_1698/ABSENT, evidence_65:account_2437/ABSENT, evidence_65:account_2480/ABSENT, evidence_65:account_3653/PRESENT, evidence_65:account_7023/ABSENT | evidence_44 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_65 |
| case_467 | evidence_65 | evidence_65:account_1698/ABSENT, evidence_65:account_2437/ABSENT, evidence_65:account_2480/ABSENT, evidence_65:account_3653/PRESENT, evidence_65:account_7023/ABSENT | evidence_44 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_65 |
| case_470 | evidence_65 | evidence_65:account_1698/ABSENT, evidence_65:account_2437/ABSENT, evidence_65:account_2480/ABSENT, evidence_65:account_3653/PRESENT, evidence_65:account_7023/ABSENT | evidence_44 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_65 |
| case_480 | evidence_45 | evidence_45:account_1433/ABSENT, evidence_45:account_2961/ABSENT, evidence_45:account_3378/ABSENT, evidence_45:account_3589/ABSENT, evidence_45:account_4036/ABSENT, evidence_45:account_5293/PRESENT, evidence_45:account_6654/PRESENT, evidence_45:account_7455/ABSENT, evidence_45:account_9031/ABSENT, evidence_45:account_9031/PRESENT, evidence_45:account_9398/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_45 |
| case_493 | evidence_63 | evidence_63:account_3626/PRESENT, evidence_63:account_634/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_63 |
| case_494 | evidence_63 | evidence_63:account_3626/PRESENT, evidence_63:account_634/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_63 |
| case_497 | evidence_63 | evidence_63:account_3626/PRESENT, evidence_63:account_634/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_63 |
| case_502 | evidence_63 | evidence_63:account_3626/PRESENT, evidence_63:account_634/PRESENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_63 |
| case_506 | evidence_47 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_47 |
| case_512 | evidence_47 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_47 |
| case_524 | evidence_62 | evidence_62:account_2424/PRESENT, evidence_62:account_470/ABSENT, evidence_62:account_4974/PRESENT, evidence_62:account_6169/ABSENT, evidence_62:account_704/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_62 |
| case_530 | evidence_62 | evidence_62:account_2424/PRESENT, evidence_62:account_470/ABSENT, evidence_62:account_4974/PRESENT, evidence_62:account_6169/ABSENT, evidence_62:account_704/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_62 |
| case_532 | evidence_62 | evidence_62:account_2424/PRESENT, evidence_62:account_470/ABSENT, evidence_62:account_4974/PRESENT, evidence_62:account_6169/ABSENT, evidence_62:account_704/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_62 |
| case_55 | evidence_32 | none | evidence_01 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | primary evidence search only |
| case_57 | evidence_05 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_05 |
| case_58 | evidence_05 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_05 |
| case_59 | evidence_05 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_05 |
| case_60 | evidence_05 | none | none | NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES | evidence_05 |
| case_64 | evidence_93 | evidence_93:account_9079/PRESENT | evidence_06 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_93 |
| case_69 | evidence_93 | evidence_93:account_9079/PRESENT | evidence_06 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_93 |
| case_70 | evidence_93 | evidence_93:account_9079/PRESENT | evidence_06 | ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE | evidence_93 |
| case_97 | evidence_89 | evidence_89:account_4421/PRESENT, evidence_89:account_6813/ABSENT | none | MISSING_SUBJECT_TO_RESOURCE_LINK | evidence_89 |

## case_55: four separate facts

| Proposition | Evidence examined | Result |
|---|---|---|
| Archive exists | evidence_32 original PNG, OCR and visual reinspection | Established for backup_9287 |
| Archive is linked to this subject | activity_4006 before cutoff, plus matching archive/contact field in the PNG | Catalog-supported association established |
| This archive is technically restorable | Storage size, encryption and a last-drill field; neighboring archives restored in the activity panel | Not established for this archive; the listed drill predates this archive's creation |
| Restore access was allowed/blocked at cutoff | All 27 eligible manifest sources and pre-cutoff CSV activities searched | No explicit configuration/access proof found |

The cutoff is 2026-04-30T11:00:00Z. The PNG capture and catalog linkage precede it. The later activity_3387 and later log/SQL captures are excluded. Generic restore-success percentages and a neighboring archive's restore are not used to infer permission for backup_9287. This case stays unresolved.

## P5 boundary and P7 decision

A bounded optional intent adapter is implemented and tested with mocked provider transport. Real model discovery returned HTTP 401; no usable live model was verified, no live inference calls were made, and no model/token/pricing identifier was fabricated. Live AI quality is NOT VERIFIED. The full dataset stays on deterministic inference and local OCR.

The final output gate remains FAIL because 518 supported predictions do not exist. The validated partial artifact and development ZIP remain separate from a finished submission. No unknown case is recast as NOT_APPLICABLE, no unsupported COMPLETE is forced, and no HackerRank upload occurred.
