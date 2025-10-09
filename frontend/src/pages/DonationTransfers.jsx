import React from 'react';
import TransferHistory from '../components/network/TransferHistory';
import '../components/network/Network.css';

const DonationTransfers = () => {
  return (
    <div className="donation-transfers-page">
      <div className="page-header">
        <h1>Transferencias de Donaciones</h1>
        <p>Historial completo de transferencias enviadas y recibidas</p>
      </div>

      <TransferHistory />
    </div>
  );
};

export default DonationTransfers;