"use client";

import { useEffect, useState } from "react";
import { Session } from "@supabase/supabase-js";
import { supabase } from "../lib/supabaseClient";
import LoginPanel from "../components/LoginPanel";
import Dashboard from "../components/Dashboard";

export default function HomePage() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data.session ?? null);
      setLoading(false);
    };

    const { data: subscription } = supabase.auth.onAuthStateChange((_, newSession) => {
      setSession(newSession);
    });

    init();

    return () => {
      subscription.subscription.unsubscribe();
    };
  }, []);

  if (loading) {
    return <div style={{ padding: 32 }}>Carregando...</div>;
  }

  if (!session) {
    return <LoginPanel />;
  }

  return <Dashboard managerId={session.user.email} />;
}
