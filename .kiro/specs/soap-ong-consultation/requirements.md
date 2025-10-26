# Requirements Document

## Introduction

The NGO network has made available a SOAP service to query data about presidents of other NGOs adhered to the network and another different endpoint to view NGO data, using the organization ID. A new screen needs to be developed through which there will be an input to send a list of organization IDs from which we want to obtain the data of their presidents and the data of the NGOs they belong to. The SOAP query only requires a client, no server development is needed.

## Glossary

- **SOAP Service**: External web service that provides data about NGO presidents and organizations
- **Organization ID**: Unique identifier for each NGO in the network
- **President Data**: Information about the president of an NGO including name, address, and phone
- **NGO Data**: Information about an organization including name, address, and phone
- **WSDL**: Web Services Description Language document that describes the SOAP service interface
- **Frontend Interface**: User interface component that allows input of organization IDs and displays results

## Requirements

### Requirement 1

**User Story:** As a President user, I want to access a new screen for SOAP consultation, so that I can query information about other NGOs and their presidents in the network.

#### Acceptance Criteria

1. WHEN a President user accesses the system, THE system SHALL provide a new menu option for "NGO Network Consultation"
2. WHEN the President clicks on the NGO Network Consultation option, THE system SHALL display a dedicated screen for SOAP queries
3. WHEN the consultation screen loads, THE system SHALL show an input field for entering organization IDs
4. WHEN the consultation screen loads, THE system SHALL display clear instructions on how to use the interface
5. WHERE the user has President role, THE system SHALL allow access to the SOAP consultation feature

### Requirement 2

**User Story:** As a President user, I want to input a list of organization IDs, so that I can specify which NGOs I want to query information about.

#### Acceptance Criteria

1. WHEN the user is on the SOAP consultation screen, THE system SHALL provide an input field that accepts multiple organization IDs
2. WHEN the user enters organization IDs, THE system SHALL accept comma-separated values or line-separated values
3. WHEN the user enters invalid characters, THE system SHALL validate that only numeric IDs are accepted
4. WHEN the user submits empty input, THE system SHALL display a validation message requiring at least one organization ID
5. WHEN the user enters duplicate IDs, THE system SHALL automatically remove duplicates before processing

### Requirement 3

**User Story:** As a President user, I want to query president information from the SOAP service, so that I can see details about presidents of other NGOs in the network.

#### Acceptance Criteria

1. WHEN the user submits organization IDs, THE system SHALL call the "list_presidents" SOAP operation
2. WHEN calling the SOAP service, THE system SHALL include proper authentication headers with Grupo "GrupoA-TM" and Clave "clave-tm-a"
3. WHEN the SOAP call is successful, THE system SHALL parse the XML response and extract president information
4. WHEN president data is received, THE system SHALL display president ID, name, address, phone, and organization_id for each result
5. IF the SOAP service returns an error, THEN THE system SHALL display an appropriate error message to the user

### Requirement 4

**User Story:** As a President user, I want to query organization information from the SOAP service, so that I can see details about NGOs in the network.

#### Acceptance Criteria

1. WHEN the user submits organization IDs, THE system SHALL call the "list_associations" SOAP operation
2. WHEN calling the SOAP service, THE system SHALL include proper authentication headers with Grupo "GrupoA-TM" and Clave "clave-tm-a"
3. WHEN the SOAP call is successful, THE system SHALL parse the XML response and extract organization information
4. WHEN organization data is received, THE system SHALL display organization ID, name, address, and phone for each result
5. IF the SOAP service returns an error, THEN THE system SHALL display an appropriate error message to the user

### Requirement 5

**User Story:** As a President user, I want to see both president and organization data together, so that I can have complete information about each NGO in a single view.

#### Acceptance Criteria

1. WHEN both SOAP calls are completed successfully, THE system SHALL combine the results by organization ID
2. WHEN displaying results, THE system SHALL show organization information alongside its corresponding president information
3. WHEN an organization has no president data, THE system SHALL still display the organization information with a note about missing president data
4. WHEN a president exists but organization data is missing, THE system SHALL display the president information with a note about missing organization data
5. WHEN displaying combined data, THE system SHALL organize results in a clear, readable format such as cards or tables

### Requirement 6

**User Story:** As a President user, I want proper error handling and loading states, so that I have a good user experience when using the SOAP consultation feature.

#### Acceptance Criteria

1. WHEN SOAP calls are in progress, THE system SHALL display a loading indicator to inform the user
2. WHEN the SOAP service is unavailable, THE system SHALL display a clear error message indicating connectivity issues
3. WHEN authentication fails, THE system SHALL display an error message about authentication problems
4. WHEN invalid organization IDs are provided, THE system SHALL display validation errors before making SOAP calls
5. WHEN network timeouts occur, THE system SHALL display a timeout error message and suggest retrying

### Requirement 7

**User Story:** As a system administrator, I want the SOAP client to be properly configured, so that it can successfully communicate with the external SOAP service.

#### Acceptance Criteria

1. WHEN the system initializes, THE system SHALL configure the SOAP client to use the WSDL URL "https://soap-app-latest.onrender.com/?wsdl"
2. WHEN making SOAP calls, THE system SHALL set the Content-Type header to "text/xml; charset=utf-8"
3. WHEN making SOAP calls, THE system SHALL include the appropriate SOAPAction header for each operation
4. WHEN constructing SOAP envelopes, THE system SHALL use the correct XML namespaces as specified in the WSDL
5. WHEN handling SOAP responses, THE system SHALL properly parse XML and handle different response formats

### Requirement 8

**User Story:** As a developer, I want the SOAP integration to be maintainable and testable, so that it can be easily updated and debugged when needed.

#### Acceptance Criteria

1. WHEN implementing the SOAP client, THE system SHALL separate SOAP logic into dedicated service modules
2. WHEN implementing SOAP operations, THE system SHALL create reusable functions for each SOAP method
3. WHEN handling SOAP responses, THE system SHALL implement proper XML parsing with error handling
4. WHEN logging SOAP interactions, THE system SHALL log requests and responses for debugging purposes
5. WHEN testing SOAP functionality, THE system SHALL provide mock capabilities for testing without external dependencies