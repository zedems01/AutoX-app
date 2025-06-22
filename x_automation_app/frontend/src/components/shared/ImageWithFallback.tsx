"use client"

import { useState } from "react"
import Image, { ImageProps } from "next/image"

interface ImageWithFallbackProps extends ImageProps {
  fallbackSrc: string
}

export function ImageWithFallback({
  src,
  fallbackSrc,
  ...props
}: ImageWithFallbackProps) {
  const [error, setError] = useState(false)

  const handleError = () => {
    setError(true)
  }

  return (
    <Image
      src={error ? fallbackSrc : src}
      onError={handleError}
      {...props}
    />
  )
} 