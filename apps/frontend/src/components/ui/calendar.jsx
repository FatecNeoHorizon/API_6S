import * as React from "react"
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react"
import { DayPicker } from "react-day-picker"

import "react-day-picker/dist/style.css"
import "@/index.css" // Ensure base classes are present if needed
import { cn } from "../../utils/utils"
// import { buttonVariants } from "./button" // We won't need this if we use default styles

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}) {
  return (
    <div className={cn("p-3 bg-card text-card-foreground rounded-md", className)}>
      <DayPicker
        showOutsideDays={showOutsideDays}
        className="react-day-picker-custom"
        // In v9, many classes like `rdp-day` are built-in from style.css
        // We will just let react-day-picker handle its own stylesheet
        {...props}
      />
      <style dangerouslySetInnerHTML={{__html: `
        .react-day-picker-custom {
          --rdp-accent-color: hsl(var(--primary));
          --rdp-background-color: hsl(var(--accent));
          --rdp-text-color: hsl(var(--foreground));
          --rdp-outline: 2px solid hsl(var(--ring));
          --rdp-range_middle-background-color: hsl(var(--primary) / 0.15);
          --rdp-range_middle-color: hsl(var(--foreground));
        }
        
        /* Override Tailwind's button background reset */
        .react-day-picker-custom .rdp-range_start,
        .react-day-picker-custom .rdp-range_end,
        .react-day-picker-custom .rdp-day_selected {
          background-color: hsl(var(--primary)) !important;
          color: hsl(var(--primary-foreground)) !important;
          border-radius: 50% !important;
        }

        .react-day-picker-custom .rdp-range_middle {
          background-color: hsl(var(--primary) / 0.15) !important;
          color: hsl(var(--foreground)) !important;
          border-radius: 0 !important;
        }
      `}} />
    </div>
  )
}
Calendar.displayName = "Calendar"

export { Calendar }
