import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ImageWithFallback } from '@/components/shared/ImageWithFallback';

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
    return <img {...props} />;
  },
}));

describe('ImageWithFallback Component', () => {
  it('should render image with correct src', () => {
    render(
      <ImageWithFallback
        src="/test-image.jpg"
        fallbackSrc="/fallback.jpg"
        alt="Test image"
        width={100}
        height={100}
      />
    );

    const image = screen.getByAltText('Test image');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', '/test-image.jpg');
  });

  it('should show fallback image on error', () => {
    render(
      <ImageWithFallback
        src="/broken-image.jpg"
        fallbackSrc="/fallback.jpg"
        alt="Test image"
        width={100}
        height={100}
      />
    );

    const image = screen.getByAltText('Test image');
    
    // Simulate image load error
    fireEvent.error(image);

    expect(image).toHaveAttribute('src', '/fallback.jpg');
  });

  it('should pass through other props to Image', () => {
    render(
      <ImageWithFallback
        src="/test-image.jpg"
        fallbackSrc="/fallback.jpg"
        alt="Test image"
        width={200}
        height={200}
        className="custom-class"
      />
    );

    const image = screen.getByAltText('Test image');
    expect(image).toHaveAttribute('width', '200');
    expect(image).toHaveAttribute('height', '200');
    expect(image).toHaveClass('custom-class');
  });
});

