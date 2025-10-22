import { gql } from '@apollo/client';

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
        id
        categoria
        descripcion
        cantidad
        eliminado
        fechaAlta
        usuarioAlta {
          id
          nombre
          email
        }
        fechaModificacion
        usuarioModificacion {
          id
          nombre
          email
        }
      }
    }
  }
`;

// Query para obtener filtros guardados de donaciones
export const GET_SAVED_DONATION_FILTERS = gql`
  query GetSavedDonationFilters {
    savedDonationFilters {
      id
      nombre
      filtros
      fechaCreacion
    }
  }
`;

// Mutation para guardar filtro de donaciones
export const SAVE_DONATION_FILTER = gql`
  mutation SaveDonationFilter($nombre: String!, $filtros: DonationFilterInput!) {
    saveDonationFilter(nombre: $nombre, filtros: $filtros) {
      id
      nombre
      filtros
      fechaCreacion
    }
  }
`;

// Mutation para actualizar filtro de donaciones
export const UPDATE_DONATION_FILTER = gql`
  mutation UpdateDonationFilter($id: ID!, $nombre: String, $filtros: DonationFilterInput) {
    updateDonationFilter(id: $id, nombre: $nombre, filtros: $filtros) {
      id
      nombre
      filtros
      fechaCreacion
    }
  }
`;

// Mutation para eliminar filtro de donaciones
export const DELETE_DONATION_FILTER = gql`
  mutation DeleteDonationFilter($id: ID!) {
    deleteDonationFilter(id: $id)
  }
`;