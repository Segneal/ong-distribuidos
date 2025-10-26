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

// Query para obtener filtros guardados de transferencias
export const GET_SAVED_TRANSFER_FILTERS = gql`
  query GetSavedTransferFilters {
    savedTransferFilters {
      id
      nombre
      filtros {
        tipo
        fechaDesde
        fechaHasta
        estado
      }
      fechaCreacion
    }
  }
`;

// Mutation para guardar filtro de transferencias
export const SAVE_TRANSFER_FILTER = gql`
  mutation SaveTransferFilter(
    $nombre: String!
    $tipo: String
    $fechaDesde: String
    $fechaHasta: String
    $estado: String
  ) {
    saveTransferFilter(
      nombre: $nombre
      filtros: {
        tipo: $tipo
        fechaDesde: $fechaDesde
        fechaHasta: $fechaHasta
        estado: $estado
      }
    ) {
      id
      nombre
      filtros {
        tipo
        fechaDesde
        fechaHasta
        estado
      }
      fechaCreacion
    }
  }
`;

// Mutation para actualizar filtro de transferencias
export const UPDATE_TRANSFER_FILTER = gql`
  mutation UpdateTransferFilter(
    $id: String!
    $nombre: String
    $tipo: String
    $fechaDesde: String
    $fechaHasta: String
    $estado: String
  ) {
    updateTransferFilter(
      id: $id
      nombre: $nombre
      filtros: {
        tipo: $tipo
        fechaDesde: $fechaDesde
        fechaHasta: $fechaHasta
        estado: $estado
      }
    ) {
      id
      nombre
      filtros {
        tipo
        fechaDesde
        fechaHasta
        estado
      }
      fechaCreacion
    }
  }
`;

// Mutation para eliminar filtro de transferencias
export const DELETE_TRANSFER_FILTER = gql`
  mutation DeleteTransferFilter($id: String!) {
    deleteTransferFilter(id: $id)
  }
`;