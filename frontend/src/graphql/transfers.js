import { gql } from '@apollo/client';

export const GET_TRANSFER_REPORT = gql`
  query GetTransferReport(
    $tipo: String
    $fechaDesde: String
    $fechaHasta: String
    $estado: String
  ) {
    transferReport(
      tipo: $tipo
      fechaDesde: $fechaDesde
      fechaHasta: $fechaHasta
      estado: $estado
    ) {
      organizacion
      tipo
      totalTransferencias
      totalItems
      transferencias {
        id
        tipo
        organizacionContraparte
        organizacionPropietaria
        solicitudId
        donaciones {
          categoria
          descripcion
          cantidad
          inventoryId
        }
        estado
        fechaTransferencia
        usuarioRegistro
        notas
        totalItems
        totalQuantity
      }
    }
  }
`;