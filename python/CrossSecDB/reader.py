from . import XSecConnection

def get_xsec(samples, cnf=None, energy=13):
    """
    Get the cross sections from the central database.
    Can be a list or a single sample.
    """

    if not isinstance(samples, list):
        return get_xsec([samples], cnf)

    # Connect. Default to Dan's xsec configuration on the T3.
    # Otherwise, use the passed cnf or the environment variable XSECCONF

    conn = XSecConnection(write=False, cnf=cnf)

    output = []

    for sample in samples:
        conn.curs.execute('SELECT cross_section FROM xs_%sTeV WHERE sample=%s',
                          (energy, sample))

        output.append(conn.curs.fetchone()[0])

    # Give people behavior they would expect
    if len(output) == 1:
        return output[0]

    return output
