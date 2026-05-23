MODEL (
  name bronze.sba_loans,
  kind FULL,
  description 'Bronze layer: SBA 7(a) and 504 loan data for Middle Tennessee counties'
);

SELECT
  strptime(asofdate, '%m/%d/%Y')::DATE  AS as_of_date,
  program                       AS program_type,
  borrname                      AS borrower_name,
  borrcity                      AS borrower_city,
  borrstate                     AS borrower_state,
  borrzip                       AS borrower_zip,
  projectcounty                 AS project_county,
  projectstate                  AS project_state,
  CAST(grossapproval AS DOUBLE)         AS gross_approval_amount,
  CAST(sbaguaranteedapproval AS DOUBLE) AS sba_guaranteed_amount,
  strptime(approvaldate, '%-m/%-d/%Y')::DATE  AS approval_date,
  approvalfiscalyear            AS approval_fiscal_year,
  naicscode                     AS naics_code,
  naicsdescription              AS naics_description,
  businesstype                  AS business_type,
  businessage                   AS business_age,
  loanstatus                    AS loan_status,
  CAST(jobssupported AS INTEGER) AS jobs_supported,
  CAST(terminmonths AS INTEGER) AS term_months,
  program_type                  AS source_program,
  CURRENT_TIMESTAMP             AS ingested_at
FROM read_json_auto('raw_data/sba/sba_midtenn_*.json')
WHERE strptime(approvaldate, '%-m/%-d/%Y')::DATE >= '2019-01-01'
