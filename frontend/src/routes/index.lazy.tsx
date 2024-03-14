import { PrivateRoute } from "@/components/hoc/PrivateRoute";
import { ChatPage } from "@/components/pages/Chat/sections/Page";
import { createFileRoute } from "@tanstack/react-router";

const Index = () => {
  return (
    <PrivateRoute>
      <ChatPage />
    </PrivateRoute>
  );
};

export const Route = createFileRoute("/")({
  component: () => <Index />
});
