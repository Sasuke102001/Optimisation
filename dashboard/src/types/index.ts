export interface Table {
  id: string            // mapped to tableId (e.g. "T7")
  cap: number           // capacity
  occupied: boolean
  pplCount: number | '6+' | null
  custType: string | null
  note: string
  seatedTime: number | null // timestamp
}

export interface IntervalRecord {
  time: string
  entries: number
  exits: number
}

export interface KPISignal {
  signalName: string
  sourceType: 'manual' | 'counter' | 'derived' | 'sensor'
  status: 'ok' | 'watch' | 'alert'
}

export interface KPIFamily {
  id: string
  name: string
  icon: string
  desc: string
  signals: string[]
}

export interface Suggestion {
  id: string
  title: string
  body: string
  priority: 1 | 2 | 3 | 4 | 5
  status: 'pending' | 'shown' | 'acted' | 'dismissed' | 'expired'
  generatedAt: number
}

export interface Complaint {
  type: string
  severity: 'watch' | 'alert'
  zone: string
  note: string
  timestamp: number
}

export type SessionMode = 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP';
export type RAGStatus = 'ok' | 'watch' | 'alert' | 'stale' | 'none';
