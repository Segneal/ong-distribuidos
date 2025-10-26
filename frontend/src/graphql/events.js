import { gql } from '@apollo/client';
import { USER_FRAGMENT } from './types';

// Fragment for event detail information
export const EVENT_DETAIL_FRAGMENT = gql`
  fragment EventDetailInfo on EventDetailType {
    dia
    nombre
    descripcion
    participantes {
      id
      nombre
      apellido
      rol
      fechaAdhesion
    }
    donaciones {
      id
      categoria
      descripcion
      cantidad
      eliminado
      fechaAlta
      usuarioAlta {
        ...UserInfo
      }
    }
  }
  ${USER_FRAGMENT}
`;

// Query para obtener reportes de participación en eventos
export const GET_EVENT_PARTICIPATION_REPORT = gql`
  query GetEventParticipationReport(
    $usuarioId: Int!
    $fechaDesde: String
    $fechaHasta: String
    $repartodonaciones: Boolean
  ) {
    eventParticipationReport(
      usuarioId: $usuarioId
      fechaDesde: $fechaDesde
      fechaHasta: $fechaHasta
      repartodonaciones: $repartodonaciones
    ) {
      mes
      eventos {
        ...EventDetailInfo
      }
    }
  }
  ${EVENT_DETAIL_FRAGMENT}
`;

// Query para obtener filtros guardados de eventos
export const GET_SAVED_EVENT_FILTERS = gql`
  query GetSavedEventFilters {
    savedEventFilters {
      id
      nombre
      filtros {
        usuarioId
        fechaDesde
        fechaHasta
        repartodonaciones
      }
      fechaCreacion
    }
  }
`;

// Mutation para guardar filtro de eventos
export const SAVE_EVENT_FILTER = gql`
  mutation SaveEventFilter(
    $nombre: String!
    $usuarioId: Int
    $fechaDesde: String
    $fechaHasta: String
    $repartodonaciones: Boolean
  ) {
    saveEventFilter(
      nombre: $nombre
      filtros: {
        usuarioId: $usuarioId
        fechaDesde: $fechaDesde
        fechaHasta: $fechaHasta
        repartodonaciones: $repartodonaciones
      }
    ) {
      id
      nombre
      filtros {
        usuarioId
        fechaDesde
        fechaHasta
        repartodonaciones
      }
      fechaCreacion
    }
  }
`;

// Mutation para actualizar filtro de eventos
export const UPDATE_EVENT_FILTER = gql`
  mutation UpdateEventFilter(
    $id: String!
    $nombre: String
    $usuarioId: Int
    $fechaDesde: String
    $fechaHasta: String
    $repartodonaciones: Boolean
  ) {
    updateEventFilter(
      id: $id
      nombre: $nombre
      filtros: {
        usuarioId: $usuarioId
        fechaDesde: $fechaDesde
        fechaHasta: $fechaHasta
        repartodonaciones: $repartodonaciones
      }
    ) {
      id
      nombre
      filtros {
        usuarioId
        fechaDesde
        fechaHasta
        repartodonaciones
      }
      fechaCreacion
    }
  }
`;

// Mutation para eliminar filtro de eventos
export const DELETE_EVENT_FILTER = gql`
  mutation DeleteEventFilter($id: String!) {
    deleteEventFilter(id: $id)
  }
`;

// Query para obtener usuarios de la organización
export const GET_ORGANIZATION_USERS = gql`
  query GetOrganizationUsers {
    organizationUsers {
      id
      nombre
      apellido
      rol
      activo
    }
  }
`;