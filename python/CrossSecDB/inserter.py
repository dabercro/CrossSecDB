from . import XSecConnection

class BadInput(Exception):
    pass

def put_xsec(samples, cross_sections, source, comments='', cnf=None, energy=13):
    """
    Places samples with parallel list, cross_sections into database.
    Source of the cross sections must be given.
    Comments are optional, but can be useful.
    """

    # Pass lists to keep rest of logic clean

    if not isinstance(samples, list):
        return put_xsec([samples], cross_sections, source, comments, cnf)
    if not isinstance(cross_sections, list):
        return put_xsec(samples, [cross_sections], source, comments, cnf)

    # Check inputs

    if not source:
        raise BadInput('Source of cross sections recommended for proper documentation.')
    if len(samples) != len(cross_sections):
        raise BadInput('Samples and cross sections are different length lists.')
    if cnf and not os.path.exists(cnf):
        raise BadInput('Configuration file %s does not exist', cnf)

    # Connect. Default to Dan's xsec configuration on the T3.
    # Otherwise, use the passed cnf or the environment variable XSECCONF

    many_input = [(sample, xs, source, comments) \
                      for sample, xs in zip(samples, cross_sections)]

    conn = XSecConnection(write=False, cnf=cnf)

    statement = """
                INSERT INTO xs_{0}TeV (sample, cross_section, last_updated, source, comments)
                VALUES (%s, %s, NOW(), %s, %s)
                """.format(energy)
    
    conn.curs.executemany(statement, many_input)
