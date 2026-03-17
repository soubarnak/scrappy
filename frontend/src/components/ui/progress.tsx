"use client";
import * as React from "react";
import { Progress as ProgressPrimitive } from "radix-ui";
import { cn } from "@/lib/utils";

interface ProgressProps extends React.ComponentProps<typeof ProgressPrimitive.Root> {
  indeterminate?: boolean;
}

function Progress({ className, value, indeterminate, ...props }: ProgressProps) {
  return (
    <ProgressPrimitive.Root
      className={cn(
        "relative h-1.5 w-full overflow-hidden rounded-full bg-primary/15",
        className
      )}
      {...props}
    >
      <ProgressPrimitive.Indicator
        className={cn(
          "h-full bg-primary transition-transform duration-500",
          indeterminate && "animate-[indeterminate_1.5s_ease-in-out_infinite]"
        )}
        style={
          indeterminate
            ? { width: "40%", transform: "translateX(-100%)" }
            : { transform: `translateX(-${100 - (value || 0)}%)`, width: "100%" }
        }
      />
    </ProgressPrimitive.Root>
  );
}

export { Progress };
