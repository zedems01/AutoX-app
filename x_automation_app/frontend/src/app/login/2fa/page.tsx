"use client"

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/components/ui/input-otp"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { completeLogin } from "@/lib/api"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

const formSchema = z.object({
  two_fa_code: z.string().min(6, {
    message: "Your one-time password must be 6 characters.",
  }),
})

export default function TwoFactorAuthPage() {
  const router = useRouter()
  const { threadId } = useWorkflowContext()

  useEffect(() => {
    if (!threadId) {
      toast.error("No active login session. Please start again.")
      router.replace("/login")
    }
  }, [threadId, router])

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      two_fa_code: "",
    },
  })

  const mutation = useMutation({
    mutationFn: completeLogin,
    onSuccess: (data) => {
      toast.success("Login successful!")
      console.log("Logged in user:", data.user_details)
      router.push("/") // Navigate to main configuration page
    },
    onError: (error) => {
      toast.error(`Login failed: ${error.message}`)
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    if (!threadId) {
      toast.error("Session expired. Please log in again.")
      return
    }
    mutation.mutate({ thread_id: threadId, two_fa_code: values.two_fa_code })
  }

  return (
    <div className="flex justify-center pt-10">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
          <CardDescription>
            Please enter the code from your authentication app.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="two_fa_code"
                render={({ field }) => (
                  <FormItem className="flex flex-col items-center">
                    <FormLabel>One-Time Password</FormLabel>
                    <FormControl>
                      <InputOTP maxLength={6} {...field}>
                        <InputOTPGroup>
                          <InputOTPSlot index={0} />
                          <InputOTPSlot index={1} />
                          <InputOTPSlot index={2} />
                          <InputOTPSlot index={3} />
                          <InputOTPSlot index={4} />
                          <InputOTPSlot index={5} />
                        </InputOTPGroup>
                      </InputOTP>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Verify Code
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
} 