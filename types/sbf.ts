// SPDX-License-Identifier: Apache-2.0
export type SpecTag = "SBF v0.1";
export type Level = "L0" | "L1" | "L2" | "L3" | "L4" | "L5";
type Brand<K, T> = K & { __brand: T };
export type CharId = Brand<string, "CharId">;
export type EntId  = Brand<string, "EntId">;
export type BeatId = Brand<string, "BeatId">;
export interface BaseDoc { spec: SpecTag; spec_version?: string; lang?: string; a_schema?: string; links?: {rel:string; src:string; tgt:string;}[]; l: Level; t: string; k?: Record<string, unknown>; dict?: { s?: string[]; q?: string[] }; features?: ("style"|"themes"|"quotes"|"text_map")[]; }
export interface Actn { p?: CharId; a?: string; u?: CharId | EntId; i?: string | null; loc?: EntId; when?: string | null; time?: { kind:'ordinal'|'iso'; episode?: number|null; scene?: number|null; beat?: number|null; start?: string|null; end?: string|null; }; }
export interface BeatRec { id: BeatId; act?: number | null; evt?: string; evt_si?: number; actn?: Actn; }
export type BeatRow = [BeatId, number, number | null, CharId | null, string | null, (CharId|EntId) | null, string | null, EntId | null, string | null];
export interface BeatsTbl { cols: ["id","act","evt_si","p","a","u","i","loc","when"]; rows: BeatRow[]; }
export interface CharRec { id: CharId; r?: string; n?: string | Record<string,string>; n_si?: number; pro?: string; }
export type CharRow = [CharId, string, number, string];
export interface CharsTbl { cols: ["id","r","n_si","pro"]; rows: CharRow[]; }
export interface SbfL1 extends BaseDoc { l: "L1"; beats?: BeatRec[]; chars?: CharRec[]; ents?: CharRec[]; }
export interface SbfL2 extends BaseDoc { l: "L2"; beats?: BeatRec[]; chars?: CharRec[]; ents?: CharRec[]; }
export interface SbfL3 extends BaseDoc { l: "L3"; beats_tbl?: BeatsTbl; chars_tbl?: CharsTbl; }
export interface SbfL4 extends BaseDoc { l: "L4"; beats?: BeatRec[]; beats_tbl?: BeatsTbl; style?: any; themes?: any; quotes?: any; motifs?: any; }
export interface SbfL5 extends BaseDoc { l: "L5"; text_map?: any; }
export type SbfDoc = SbfL1 | SbfL2 | SbfL3 | SbfL4 | SbfL5;
