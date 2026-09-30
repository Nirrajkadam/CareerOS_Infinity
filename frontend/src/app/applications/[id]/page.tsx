import React from 'react';
import ApplicationDetailClient from './ApplicationDetailClient';

export function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: 'demo' },
  ];
}

export default function ApplicationDetailPage({ params }: { params: { id: string } }) {
  return <ApplicationDetailClient params={params} />;
}
