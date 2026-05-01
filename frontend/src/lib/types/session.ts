export interface Session {
  id: number;
  session_id: string;
  notebook_id: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}