import { gql } from '@apollo/client';
import { USER_FRAGMENT } from './types';

// Fragment for event detail information
export const EVENT_DETAIL_FRAGMENT = gql`
  fragment EventDetailInfo on EventDetailType {
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