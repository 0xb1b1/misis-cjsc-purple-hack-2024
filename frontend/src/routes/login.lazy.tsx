import { LoginPage } from "@/components/pages/Login/LoginPage";
import { createFileRoute } from "@tanstack/react-router";

interface LoginSearch {
  redirect: string;
}

export const Route = createFileRoute("/login")({
  component: LoginPage,
  validateSearch: (search: Record<string, unknown>): LoginSearch => {
    return {
      redirect: search.redirect ? String(search.redirect) : "/"
    };
  }
});
