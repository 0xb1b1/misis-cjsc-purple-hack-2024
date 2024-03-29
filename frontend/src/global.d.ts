import { HTMLProps } from "react";

declare module "*.svg" {
  const svg: React.FC<HTMLProps<SVGElement>>;
  export default svg;
}
