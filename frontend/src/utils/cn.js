/**
 * Utility function to combine class names
 * Similar to clsx or classnames but simpler
 */
export function cn(...classes) {
  return classes
    .filter(Boolean)
    .join(' ')
    .trim();
}
