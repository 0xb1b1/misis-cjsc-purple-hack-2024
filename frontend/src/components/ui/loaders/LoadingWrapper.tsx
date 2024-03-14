import LoadingEllipsis from "./LoadingEllipsis";

export const LoadingWrapper = () => {
  return (
    <div className="flex justify-center items-center h-full min-h-60">
      <LoadingEllipsis />
    </div>
  );
};
