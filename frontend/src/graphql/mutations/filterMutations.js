import { gql } from '@apollo/client';

export const SAVE_DONATION_FILTER_MUTATION = gql`
  mutation SaveDonationFilter($nombre: String!, $filtros: DonationFilterInput!) {
    saveDonationFilter(nombre: $nombre, filtros: $filtros) {
      id
      nombre
      configuracion
      fechaCreacion
    }
  }
`;

export const UPDATE_DONATION_FILTER_MUTATION = gql`
  mutation UpdateDonationFilter($id: ID!, $nombre: String, $filtros: DonationFilterInput) {
    updateDonationFilter(id: $id, nombre: $nombre, filtros: $filtros) {
      id
      nombre
      configuracion
      fechaCreacion
    }
  }
`;

export const DELETE_DONATION_FILTER_MUTATION = gql`
  mutation DeleteDonationFilter($id: ID!) {
    deleteDonationFilter(id: $id)
  }
`;