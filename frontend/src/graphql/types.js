import { gql } from '@apollo/client';

// GraphQL Input Types and Fragments

// Input type for donation filters
export const DONATION_FILTER_INPUT = gql`
  input DonationFilterInput {
    categoria: String
    fechaDesde: String
    fechaHasta: String
    eliminado: Boolean
  }
`;

// Input type for event filters  
export const EVENT_FILTER_INPUT = gql`
  input EventFilterInput {
    fechaDesde: String
    fechaHasta: String
    usuarioId: ID
    repartodonaciones: Boolean
  }
`;

// Fragment for user information
export const USER_FRAGMENT = gql`
  fragment UserInfo on UserType {
    id
    nombre
    email
    rol
  }
`;

// Fragment for donation information
export const DONATION_FRAGMENT = gql`
  fragment DonationInfo on DonationType {
    id
    categoria
    descripcion
    cantidad
    eliminado
    fechaAlta
    fechaModificacion
    usuarioAlta {
      ...UserInfo
    }
    usuarioModificacion {
      ...UserInfo
    }
  }
  ${USER_FRAGMENT}
`;

// Fragment for saved filter information
export const SAVED_FILTER_FRAGMENT = gql`
  fragment SavedFilterInfo on SavedFilterType {
    id
    nombre
    filtros
    fechaCreacion
  }
`;