import PropTypes from "prop-types";
import { cn } from "../../utils/utils";

export function Card({ className, ...props }) {
  return (
    <div
      data-slot="card"
      className={cn(
        'bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm',
        className,
      )}
      {...props}
    />
  )
}

Card.propTypes = { className: PropTypes.string }
Card.defaultProps = { className: undefined }

export function CardHeader({ className, ...props }) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        '@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6',
        className,
      )}
      {...props}
    />
  )
}

CardHeader.propTypes = { className: PropTypes.string }
CardHeader.defaultProps = { className: undefined }

export function CardTitle({ className, ...props }) {
  return (
    <div
      data-slot="card-title"
      className={cn('leading-none font-semibold', className)}
      {...props}
    />
  )
}

CardTitle.propTypes = { className: PropTypes.string }
CardTitle.defaultProps = { className: undefined }

export function CardDescription({ className, ...props }) {
  return (
    <div
      data-slot="card-description"
      className={cn('text-muted-foreground text-sm', className)}
      {...props}
    />
  )
}

CardDescription.propTypes = { className: PropTypes.string }
CardDescription.defaultProps = { className: undefined }

export function CardAction({ className, ...props }) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        'col-start-2 row-span-2 row-start-1 self-start justify-self-end',
        className,
      )}
      {...props}
    />
  )
}

CardAction.propTypes = { className: PropTypes.string }
CardAction.defaultProps = { className: undefined }

export function CardContent({ className, ...props }) {
  return (
    <div
      data-slot="card-content"
      className={cn('px-6', className)}
      {...props}
    />
  )
}

CardContent.propTypes = { className: PropTypes.string }
CardContent.defaultProps = { className: undefined }

export function CardFooter({ className, ...props }) {
  return (
    <div
      data-slot="card-footer"
      className={cn('flex items-center px-6 [.border-t]:pt-6', className)}
      {...props}
    />
  )
}

CardFooter.propTypes = { className: PropTypes.string }
CardFooter.defaultProps = { className: undefined }
