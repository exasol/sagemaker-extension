
class DatabaseQueries:
    @staticmethod
    def get_all_jobs(model_setup_params, db_conn) -> list:
        query_metadata = "SELECT JOB_NAME FROM " \
                         "{schema}.SME_METADATA_AUTOPILOT_JOBS". \
            format(schema=model_setup_params.schema_name)

        all_jobs = db_conn.execute(query_metadata).fetchall()
        return all_jobs

    @staticmethod
    def get_all_scripts(model_setup_params, db_conn) -> list:
        query_scripts = "SELECT SCRIPT_NAME FROM SYS.EXA_ALL_SCRIPTS " \
                        "WHERE SCRIPT_SCHEMA = '{schema}'". \
            format(schema=model_setup_params.schema_name.upper())

        all_scripts = db_conn.execute(query_scripts).fetchall()
        return all_scripts
