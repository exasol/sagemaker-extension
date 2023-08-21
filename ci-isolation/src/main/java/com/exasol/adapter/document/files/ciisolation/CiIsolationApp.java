package com.exasol.adapter.document.files.ciisolation;

import com.exasol.ciisolation.aws.PolicyReader;
import com.exasol.ciisolation.aws.ciuser.CiUserStack;
import com.exasol.ciisolation.aws.ciuser.CiUserStack.CiUserStackProps;

import software.amazon.awscdk.App;

/**
 * This class defines a CloudFormation stack that creates a user for the CI of this project.
 */
public class CiIsolationApp {
    public static void main(final String[] args) {
        final App app = new App();
        final PolicyReader policyReader = new PolicyReader();
        CiUserStackProps props = CiUserStack.CiUserStackProps.builder().projectName("exasol-sagemaker-extension")
                .addRequiredPermissions(
                    policyReader.readPolicyFromResources("s3-access.json"),
                    policyReader.readPolicyFromResources("sagemaker-access.json")).build();
        new CiUserStack(app, props);
        app.synth();
    }
}
