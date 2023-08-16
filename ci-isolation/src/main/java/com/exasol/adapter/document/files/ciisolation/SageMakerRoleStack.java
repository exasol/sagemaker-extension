package com.exasol.adapter.document.files.ciisolation;

import com.exasol.ciisolation.aws.TaggedStack;
import com.exasol.ciisolation.aws.ciuser.CiUserStack.CiUserStackProps;

import software.amazon.awscdk.CfnOutput;
import software.amazon.awscdk.services.iam.*;
import software.constructs.Construct;

class SageMakerRoleStack extends TaggedStack {
    SageMakerRoleStack(final Construct scope, final String id, final CiUserStackProps props) {
        super(scope, id, null, props.projectName());
        Role role = Role.Builder.create(this, "Role")
                .assumedBy(new CompositePrincipal(new ServicePrincipal("sagemaker.amazonaws.com")))
                .description(
                        "Allows SageMaker notebook instances, training jobs, and models to access S3, ECR, and CloudWatch on your behalf.")
                .build();
        tagResource(role);
        role.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName("AmazonSageMakerFullAccess"));
        CfnOutput.Builder.create(this, "sagemakerRoleName").value(role.getRoleName()).build();
    }
}
