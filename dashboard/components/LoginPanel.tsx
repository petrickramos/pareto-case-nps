"use client";

import { useState } from "react";
import { supabase } from "../lib/supabaseClient";

export default function LoginPanel() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const { error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (signInError) {
      setError(signInError.message);
    }

    setLoading(false);
  };

  return (
    <section className="login-shell">
      <h1 className="login-title">Pareto NPS Monitor</h1>
      <p className="login-subtitle">
        Acesso reservado para gestores de qualidade.
      </p>
      <form onSubmit={handleLogin}>
        <label className="text-strong">Email</label>
        <input
          className="input"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="gestor@pareto.com"
          required
        />
        <div style={{ height: 12 }} />
        <label className="text-strong">Senha</label>
        <input
          className="input"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="••••••••"
          required
        />
        {error && (
          <p style={{ color: "#b33", marginTop: 12 }}>{error}</p>
        )}
        <div style={{ height: 16 }} />
        <button className="button" type="submit" disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
      <p className="small-note" style={{ marginTop: 20 }}>
        Crie o usuário no Supabase Auth antes do primeiro acesso.
      </p>
    </section>
  );
}
