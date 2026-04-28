export interface CreateNotebookPayload {
  title: string;
  description: string;
}

export type NotebookListItem = {
  notebook_id: string;
  title: string;
  description?: string;
  created_at: string; // ✅ ADD THIS
};