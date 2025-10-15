import { gql } from '@apollo/client';

export const EVENT_PARTICIPATION_REPORT_QUERY = gql`
  query EventParticipationReport(
    $fechaDesde: DateTime
    $fechaHasta: DateTime
    $usuarioId: ID!
    $repartodonaciones: Boolean
  ) {
    eventParticipationReport(
      fechaDesde: $fechaDesde
      fechaHasta: $fechaHasta
      usuarioId: $usuarioId
      repartodonaciones: $repartodonaciones
    ) {
      mes
      eventos {
        dia
        nombre
        descripcion
        donaciones {
          id
          categoria
          descripcion
          cantidad
          eliminado
        }
      }
    }
  }
`;

export const USERS_QUERY = gql`
  query Users {
    users {
      id
      nombre
      rol
    }
  }
`;

export const SAVED_EVENT_FILTERS_QUERY = gql`
  query SavedEventFilters {
    savedEventFilters {
      id
      nombre
      configuracion
      fechaCreacion
    }
  }
`;