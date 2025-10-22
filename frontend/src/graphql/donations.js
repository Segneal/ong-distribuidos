import { gql } from '@apollo/client';
import { DONATION_FRAGMENT, SAVED_FILTER_FRAGMENT } from './types';

// Query para obtener reportes de donaciones
export const GET_DONATION_REPORT = gql`
  query GetDonationReport(
    $categoria: String
    $fechaDesde: String
    $fechaHasta: String
    $eliminado: Boolean
  ) {
    donationReport(
      categoria: $categoria
      fechaDesde: $fechaDesde
      fechaHasta: $fechaHasta
      eliminado: $eliminado
    ) {
      categoria
      eliminado
      totalCantidad
      registros {
        ...DonationInfo
      }
    }
  }
  ${DONATION_FRAGMENT}
`;

// Query para obtener filtros guardados de donaciones
export const GET_SAVED_DONATION_FILTERS = gql`
  query GetSavedDonationFilters {
    savedDonationFilters {
      ...SavedFilterInfo
    }
  }
  ${SAVED_FILTER_FRAGMENT}
`;

// Mutation para guardar filtro de donaciones
export const SAVE_DONATION_FILTER = gql`
  mutation SaveDonationFilter($nombre: String!, $filtros: DonationFilterInput!) {
    saveDonationFilter(nombre: $nombre, filtros: $filtros) {
      ...SavedFilterInfo
    }
  }
  ${SAVED_FILTER_FRAGMENT}
`;

// Mutation para actualizar filtro de donaciones
export const UPDATE_DONATION_FILTER = gql`
  mutation UpdateDonationFilter($id: ID!, $nombre: String, $filtros: DonationFilterInput) {
    updateDonationFilter(id: $id, nombre: $nombre, filtros: $filtros) {
      ...SavedFilterInfo
    }
  }
  ${SAVED_FILTER_FRAGMENT}
`;

// Mutation para eliminar filtro de donaciones
export const DELETE_DONATION_FILTER = gql`
  mutation DeleteDonationFilter($id: ID!) {
    deleteDonationFilter(id: $id)
  }
`;