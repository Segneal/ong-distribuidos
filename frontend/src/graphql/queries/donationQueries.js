import { gql } from '@apollo/client';

export const DONATION_REPORT_QUERY = gql`
  query DonationReport(
    $categoria: DonationCategory
    $fechaDesde: DateTime
    $fechaHasta: DateTime
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
        }
        fechaModificacion
        usuarioModificacion {
          id
          nombre
        }
      }
    }
  }
`;

export const SAVED_DONATION_FILTERS_QUERY = gql`
  query SavedDonationFilters {
    savedDonationFilters {
      id
      nombre
      configuracion
      fechaCreacion
    }
  }
`;