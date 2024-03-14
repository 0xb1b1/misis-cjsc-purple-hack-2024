import { LoadingWrapper } from "@/components/ui/loaders/LoadingWrapper";
import { createRootRoute, Outlet } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: () => <Outlet />,
  pendingComponent: () => <LoadingWrapper />
});
