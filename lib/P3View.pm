#
# Copyright (c) 2003-2015 University of Chicago and Fellowship
# for Interpretations of Genomes. All Rights Reserved.
#
# This file is part of the SEED Toolkit.
#
# The SEED Toolkit is free software. You can redistribute
# it and/or modify it under the terms of the SEED Toolkit
# Public License.
#
# You should have received a copy of the SEED Toolkit Public License
# along with this program; if not write to the University of Chicago
# at info@ci.uchicago.edu or the Fellowship for Interpretation of
# Genomes at veronika@thefig.info or download a copy from
# http://www.theseed.org/LICENSE.TXT.
#

# This is a SAS Component

package P3View;

    use strict;
    use warnings;
    use SeedUtils;

=head1 PATRIC Database View Manager

This module describes an object for managing a database view in the PATRIC CLI scripts. The view object
defines field-name translations for each database object in L<P3Utils>. The translations are used to map
the database fields to the fields expected by the PATRIC database API. The view object will be attached to
the L<P3DataAPI> object, and is processed by various methods in L<P3Utils> during query preparation.

To create a view object, the translations must be loaded from a file. The file is a JSON file containing a
mapping of database field names to PATRIC API field names. At the high level it is a hash from table names
to field mappings. The field mapping is itself a list of pairs. The pairs have to represent a true 1-to-1
correspondence. If a field or table is not listed in the view, it is not translated. The view object
must apply the mapping in both directions, so it is converted into a pair of hashes during load. The hashes
are stored as a list, first the forward map to the PATRIC API names and then the reverse mapping.

=head2 Public Methods

=head3 new

    my $view = P3View->new($fileName);

Create a new P3View object from the specified file. The file is a JSON file containing the view mapping,
as described above.

=over 4

=item fileName

The name of the file containing the view mapping. The file must be in JSON format.

=item table

The name of the database table for which the view is being created. This is used to load the appropriate
translations from the file.

=item RETURN

Returns a new P3View object. If the file cannot be read or is not in the correct format, an exception will be thrown.

=back

=cut

sub new {
    my ($class, $fileName, $table) = @_;
    # Default to a null mapping.
    my $self = [{},{}];
    if ($fileName) {
        my $json = SeedUtils::read_encoded_object($fileName);
        if (ref $json eq 'HASH') {
            # Get the view mapping for the specified table.
            if (!defined $table) {
                die "Table name must be specified for a P3View.";
            } else {
                my $fields = $json->{$table};
                if ($fields) {
                    my (%forward, %reverse);
                    # Process the field mappings.
                    for my $pair (@$fields) {
                        if (ref $pair eq 'ARRAY' && @$pair == 2) {
                            my ($from, $to) = @$pair;
                            if ($from && $to) {
                                $forward{$from} = $to;
                                $reverse{$to} = $from;
                            } else {
                                die "Invalid field mapping in file $fileName: from or to field is undefined.";
                            }
                        } else {
                            die "Invalid field mapping format in file $fileName: expected an array of two elements.";
                        }
                    }
                    $self = [\%forward, \%reverse];
                }
            }
        } else {
            die "Invalid view file format: expected a hash, got " . ref($json) . " in file $fileName.";
        }
    } else {
        # If no file is specified, we create a null mapping.
        $self = [{}, {}];
    }
    bless $self, $class;
    return $self;
}

=head3 col_to_internal

    my $internalName = $view->col_to_internal($colName);

Convert a field name to the internal database field name using the view mapping.

=over 4

=item colName

The user-friendly field name to convert to internal format.

=item RETURN

The internal field name corresponding to the user-friendly name. If the name is not found in the mapping,
it is returned unchanged.

=back

=cut

sub col_to_internal {
    my ($self, $colName) = @_;
    my $table = $self->[0];
    my $retVal = $table->{$colName} // $colName;  # Default to unchanged if not found.
    return $retVal;
}

=head3 internal_to_col

    my $colName = $view->internal_to_col($internalName);

Convert an internal database field name to the user-friendly field name using the view mapping.

=over 4

=item internalName

The internal field name to convert to user-friendly format.

=item RETURN

The user-friendly field name corresponding to the internal name. If the name is not found in the mapping,
it is returned unchanged.

=back

=cut

sub internal_to_col {
    my ($self, $internalName) = @_;
    my $table = $self->[1];
    my $retVal = $table->{$internalName} // $internalName;  # Default to unchanged if not found.
    return $retVal;
}

=head3 col_list_to_internaL

    my \@internalNames = $view->col_list_to_internal(\@colNames);

Convert a list of user-friendly field names to their internal database field names using the view mapping.

=over 4

=item colNames

A reference to an array of user-friendly field names to convert to internal format.

=item RETURN

A reference to an array of internal field names corresponding to the user-friendly names. If a name is not found in the mapping,
it is returned unchanged.

=back

=cut

sub col_list_to_internal {
    my ($self, $colNames) = @_;
    return [ map { $self->col_to_internal($_) } @$colNames ];
}

=head3 internal_list_to_col

    my \@colNames = $view->internal_list_to_col(\@internalNames);

Convert a list of internal database field names to their user-friendly field names using the view mapping.

=over 4

=item internalNames

A reference to an array of internal field names to convert to user-friendly format.

=item RETURN

A reference to an array of user-friendly field names corresponding to the internal names. If a name is not found in the mapping,
it is returned unchanged.

=back

=cut

sub internal_list_to_col {
    my ($self, $internalNames) = @_;
    return [ map { $self->internal_to_col($_) } @$internalNames ];
}

1;