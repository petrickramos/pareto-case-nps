import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  // eslint-disable-next-line no-console
  console.warn("Supabase env vars are missing. Check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true
  }
});

export type ConversationMessage = {
  id: string;
  chat_id: string;
  message_text: string;
  sender: "user" | "bot" | "manager" | "system";
  conversation_state: string | null;
  nps_score: number | null;
  sentiment: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type ConversationSummary = {
  chat_id: string;
  last_message: string;
  last_sender: ConversationMessage["sender"];
  last_state: string | null;
  nps_score: number | null;
  sentiment: string | null;
  updated_at: string;
};
