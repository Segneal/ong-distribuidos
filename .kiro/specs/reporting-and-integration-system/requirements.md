# Requirements Document

## Introduction

This document outlines the requirements for implementing a comprehensive reporting and integration system for the ONG management platform. The system will provide donation reports, event participation reports, custom filter management, Excel export capabilities, and SOAP integration for consulting external ONG network data. The implementation will utilize REST, GraphQL, and SOAP protocols as specified for each functionality.

## Requirements

### Requirement 1

**User Story:** As a President or Vocal, I want to view donation reports with filtering capabilities, so that I can analyze donation patterns and make informed decisions about our organization's donation activities.

#### Acceptance Criteria

1. WHEN a President or Vocal accesses the donation report screen THEN the system SHALL display a GraphQL-powered interface for querying donations
2. WHEN filtering options are provided THEN the system SHALL support filtering by category, date range (Alta), and deletion status (yes, no, or both)
3. WHEN no filters are applied THEN the system SHALL display all donation records
4. WHEN filters are applied THEN the system SHALL return results grouped by category and deletion status
5. WHEN results are displayed THEN the system SHALL show the total sum of quantities received or donated for each category
6. WHEN multiple filters are combined THEN the system SHALL apply all filters simultaneously using AND logic

### Requirement 2

**User Story:** As any user with donation report access, I want to save and manage custom filter configurations, so that I can quickly reuse frequently used search criteria without having to reconfigure them each time.

#### Acceptance Criteria

1. WHEN a user configures filters in the donation report THEN the system SHALL provide a "Save Filter" button
2. WHEN saving a filter THEN the system SHALL require the user to provide a descriptive name for the filter configuration
3. WHEN a filter is saved THEN the system SHALL store the filter configuration associated with the user's account using GraphQL mutations
4. WHEN accessing the donation report screen THEN the system SHALL display all saved filters for the current user
5. WHEN a saved filter is selected THEN the system SHALL automatically apply the stored filter configuration
6. WHEN managing saved filters THEN the system SHALL allow users to edit existing filter names and configurations
7. WHEN managing saved filters THEN the system SHALL allow users to delete unwanted filter configurations
8. WHEN a filter is deleted THEN the system SHALL remove it permanently from the user's saved filters

### Requirement 3

**User Story:** As a user viewing donation reports, I want to export the detailed data to Excel format, so that I can perform additional analysis or share the information with stakeholders outside the system.

#### Acceptance Criteria

1. WHEN viewing donation reports THEN the system SHALL provide an "Export to Excel" option via REST API
2. WHEN exporting to Excel THEN the system SHALL create separate worksheets for each donation category
3. WHEN generating Excel worksheets THEN each worksheet SHALL contain detailed records without summarization
4. WHEN displaying donation details THEN each record SHALL include: Alta date, Description, Quantity, Deletion status, Creation user, and Modification user
5. WHEN the Excel file is generated THEN the system SHALL provide a download link for the file
6. WHEN applied filters exist THEN the Excel export SHALL respect the same filtering criteria as the screen report
7. WHEN the export is complete THEN the system SHALL return a properly formatted Excel file with appropriate headers

### Requirement 4

**User Story:** As any system user, I want to view event participation reports for non-cancelled events, so that I can track member engagement and event effectiveness within our organization.

#### Acceptance Criteria

1. WHEN any user accesses the event participation report THEN the system SHALL display a GraphQL-powered interface for querying event participation
2. WHEN filtering options are provided THEN the system SHALL support filtering by date range, user, and donation distribution status (yes, no, or both)
3. WHEN a President or Coordinator applies user filters THEN the system SHALL allow selection of any user in the organization
4. WHEN a non-President/Coordinator applies user filters THEN the system SHALL restrict selection to only their own user account
5. WHEN accessing the report THEN the user filter SHALL be mandatory and cannot be left empty
6. WHEN results are displayed THEN the system SHALL group data by month
7. WHEN displaying monthly data THEN each month SHALL show event details including: day, event name, description, and associated donations
8. WHEN querying events THEN the system SHALL exclude cancelled events from all results

### Requirement 5

**User Story:** As any user with event participation report access, I want to save and manage custom filter configurations for event reports, so that I can efficiently reuse common search patterns.

#### Acceptance Criteria

1. WHEN a user configures filters in the event participation report THEN the system SHALL provide a "Save Filter" button via REST API
2. WHEN saving an event filter THEN the system SHALL require the user to provide a descriptive name for the filter configuration
3. WHEN an event filter is saved THEN the system SHALL store the filter configuration associated with the user's account
4. WHEN accessing the event participation report screen THEN the system SHALL display all saved event filters for the current user
5. WHEN a saved event filter is selected THEN the system SHALL automatically apply the stored filter configuration
6. WHEN managing saved event filters THEN the system SHALL allow users to edit existing filter names and configurations
7. WHEN managing saved event filters THEN the system SHALL allow users to delete unwanted filter configurations
8. WHEN an event filter is deleted THEN the system SHALL remove it permanently from the user's saved filters

### Requirement 6

**User Story:** As a President, I want to consult information about other ONG presidents and organizations in our network via SOAP integration, so that I can access centralized network data for coordination and collaboration purposes.

#### Acceptance Criteria

1. WHEN a President accesses the network consultation screen THEN the system SHALL provide an interface for SOAP-based queries
2. WHEN querying network data THEN the system SHALL provide an input field for entering a list of organization IDs
3. WHEN organization IDs are submitted THEN the system SHALL call the SOAP service at https://soap-applatest.onrender.com/?wsdl
4. WHEN making SOAP calls THEN the system SHALL retrieve both president data and organization data for each provided ID
5. WHEN SOAP responses are received THEN the system SHALL display the president information for each organization
6. WHEN SOAP responses are received THEN the system SHALL display the organization details for each queried ID
7. WHEN SOAP service errors occur THEN the system SHALL handle errors gracefully and display appropriate error messages
8. WHEN invalid organization IDs are provided THEN the system SHALL display appropriate validation messages

### Requirement 7

**User Story:** As a developer, I want comprehensive API documentation for the new REST endpoints, so that I can understand and integrate with the system effectively.

#### Acceptance Criteria

1. WHEN REST endpoints are implemented THEN the system SHALL provide Swagger documentation for all new REST APIs
2. WHEN accessing API documentation THEN Swagger SHALL include detailed endpoint descriptions, parameters, and response schemas
3. WHEN documenting endpoints THEN Swagger SHALL cover Excel export and custom filter management endpoints
4. WHEN API documentation is generated THEN it SHALL be accessible through a standard Swagger UI interface
5. WHEN endpoints change THEN the Swagger documentation SHALL be automatically updated to reflect current API specifications

### Requirement 8

**User Story:** As a system architect, I want the new modules to be independently deployable, so that they can be developed and maintained separately from existing system components.

#### Acceptance Criteria

1. WHEN implementing new functionality THEN the system SHALL support deployment as independent microservices
2. WHEN deploying services THEN each protocol type (REST/GraphQL/SOAP) MAY be implemented as separate microservices
3. WHEN deploying services THEN all new functionality MAY be consolidated into a single independent project
4. WHEN new modules are deployed THEN they SHALL be completely independent from existing system components
5. WHEN integrating with existing data THEN new modules SHALL access shared databases and resources through well-defined interfaces