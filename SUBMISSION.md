# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `terraform/` with your `.tf` files (the provided `userdata.sh.tftpl` stays as it is)

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste `terraform output` and the response of `curl <url>/healthz`. Which resources did Terraform create and in which order? How did it know the order?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Show how you spread the subnets over two availability zones without copying the block twice (`count`, `for_each` or both). Why are two zones the minimum for anything you call highly available?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. Your security group allows SSH from one address only. How did you get that address into Terraform without writing it in a file you commit? What happens to your access when your IP changes?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Run `terraform destroy` then `terraform apply` again and paste the end of both. Is the new public IP the same? What does that tell you about Elastic IPs and about what you hand to customers?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. Which values did you turn into variables and which are `locals`? Name one value that should never have a default.

**Your answer:**

<!-- replace this line with your answer -->

### Q6. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q7. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
