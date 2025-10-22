import { gql } from '@apollo/client';
import { USER_FRAGMENT } from './types';

// Query para obtener reportes de participación en eventos
export const GET_EVENT_PARTICIPATION_REPORT = gql`
  query GetEventParticipationReport(
    $fechaDesde: String
    $fechaHasta: String
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
          fechaAlta
          usuarioAlta {
            ...UserInfo
          }
        }
      }
    }
  }
  ${USER_FRAGMENT}
`;

// Query para obtener lista de usuarios (para el filtro)
export const GET_USERS_LIST = gql`
  query GetUsersList {
    users {
      ...UserInfo
    }
  }
  ${USER_FRAGMENT}
`;